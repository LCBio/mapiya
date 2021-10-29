import re
import os
import requests
import gzip
import numpy as np
import io
import subprocess
from collections import OrderedDict
from cached_property import cached_property
from copy import deepcopy

from mollib.vector import Vector
from mollib.selection import Selection
from mollib.utils import kabsch


class InvalidPdbCode(ValueError):

    """Exception raised when invalid pdb code is used."""

    msg = 'Invalid pdb code: {}'

    def __init__(self, code):
        self.code = code

    def __str__(self):
        return self.msg.format(self.code)


class PdbFile:

    """Class used to retrieve pdb files. Downloaded files are stored in cache for future use."""

    PDB_CACHE = os.path.join(os.path.expanduser('~'), '.PDBcache')
    RCSB_URL = 'http://files.rcsb.org/download/{}.pdb.gz'

    def __init__(self, code):
        self.code = code.lower()
        try:
            self.opened_file = gzip.open(self.filepath, 'rt')
        except FileNotFoundError:
            self.opened_file = self.fetch_from_db()
        if not self.opened_file:
            raise InvalidPdbCode(self.code)

    @cached_property
    def filepath(self):
        return os.path.join(self.PDB_CACHE, self.code[1:3], f'{self.code}.pdb.gz')

    @cached_property
    def url(self):
        return self.RCSB_URL.format(self.code)

    def fetch_from_db(self):
        request = requests.get(self.url)
        if request.status_code == 200:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'wb') as f:
                f.write(request.content)
            return gzip.open(io.BytesIO(request.content), 'rt')

    def __enter__(self):
        return self.opened_file

    def __exit__(self, *args):
        self.opened_file.close()


class DsspFile:

    DSSP_PATT = re.compile('''^
        (?P<serial>[0-9 ]{5})   # serial number
        (?P<resnum>[0-9 ]{5})   # residue number
        (?P<icode>[A-Z ])       # insertion code
        (?P<chain>[A-Z])        # chain id
        (?P<resname>.{4})       # residue name
        (?P<ss>[HBEGITS ])      # secondary structure
    ''', re.X)

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_fileobject(cls, fileobj):
        data = dict()
        for line in fileobj:
            match = re.match(cls.DSSP_PATT, line)
            if match:
                data[f'{match.group("chain")}:{int(match.group("resnum"))}{match.group("icode")}'.strip()] = \
                    'H' if match.group('ss') in 'HGI' \
                    else 'E' if match.group('ss') in 'BE' \
                    else 'T' if match.group('ss') == 'T' \
                    else 'C'
        return cls(data)

    @classmethod
    def from_filename(cls, filename):
        with open(filename, 'r') as f:
            return cls.from_fileobject(f)

    @classmethod
    def from_pdb(cls, pdb):
        proc = subprocess.run(['dssp', '/dev/stdin'], input=bytes(pdb, encoding='utf-8'), capture_output=True)
        return cls.from_fileobject(io.TextIOWrapper(io.BytesIO(proc.stdout)))


class Atom:

    """Class representing single atom."""

    # Exception raised when trying to initialize Atom instance from invalid string
    class InvalidAtomString(ValueError):
        pass

    # pattern for parsing ATOM record from the pdb file
    ATOM_PATT = re.compile('''^
        (?P<hetero>(ATOM[ ]{2}|HETATM)) # hetero
        (?P<serial>[0-9 ]{5})           # serial number
        (?P<name>[A-Z0-9' ]{5})         # name
        (?P<altloc>[A-Z ])              # alternative locator
        (?P<resname>[A-Z ]{3})          # amino acid name
        (?P<chain>[ ][A-Z])             # chain id
        (?P<resnum>[0-9 ]{4})           # residue number
        (?P<icode>[A-Z ])               # insertion code
        (?P<R>[-0-9 .]{27})             # coordinates
        (?P<occ>[-0-9 .]{6})            # occupancy
        (?P<bfac>[-0-9 .]{6})           # beta factor
    ''', re.X)

    # pattern used to check if atom is hydrogen
    HYDRO_PATT = re.compile('^(H.*|[0-9]*H.*)')

    def __init__(self, **kwargs):

        self.hetero = False
        self.serial = 0
        self.name = 'CA'
        self.altloc = ' '
        self.resname = 'UNK'
        self.chain = 'X'
        self.resnum = 0
        self.icode = ' '
        self.R = Vector()
        self.occ = 1.0
        self.bfac = 0.0
        self.model = None
        self.ss = 'C'

        for arg, val in kwargs.items():
            if hasattr(self, arg):
                attr = getattr(self, arg)
                if type(attr) is float:
                    val = float(val)
                elif type(attr) is int:
                    val = int(val)
                elif type(attr) is bool:
                    val = val == 'HETATM'
                elif type(attr) is str and val != ' ':
                    val = val.strip()
                elif isinstance(attr, Vector):
                    val = Vector(val[0:11], val[11:19], val[19:27])
                setattr(self, arg, val)
            else:
                raise TypeError(f'"{arg}" is an invalid argument for Atom()')

    def __str__(self):
        name = self.name if len(self.name) == 4 else f' {self.name:<3s}'
        hetero = 'HETATM' if self.hetero else 'ATOM  '
        return f'{hetero}{self.serial:5d} {name}{self.altloc}{self.resname:3} {self.chain}{self.resnum:4d}' \
               f'{self.icode}   {self.R.x:8.3f}{self.R.y:8.3f}{self.R.z:8.3f}{self.occ:6.2f}{self.bfac:6.2f}'

    @cached_property
    def resid(self):
        return f'{self.resnum:d}{self.icode}'.strip()

    @cached_property
    def resid_id(self):
        return f'{self.chain}:{self.resid}'

    @cached_property
    def hydro(self):
        return re.match(self.HYDRO_PATT, self.name) is not None

    @classmethod
    def from_string(cls, line):
        match = re.match(cls.ATOM_PATT, line)
        if match:
            return cls(**match.groupdict())
        else:
            raise cls.InvalidAtomString


# container for atoms
class Atoms:

    def __init__(self, atoms=()):
        self.atoms = [_ for _ in atoms]

    def __iter__(self):
        return iter(self.atoms)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Atoms(self.atoms[key])
        return self.atoms[key]

    def __setitem__(self, key, value):
        self.atoms[key] = value

    def __len__(self):
        return len(self.atoms)

    def __str__(self):
        return '\n'.join([str(atom) for atom in self])

    def index(self, item):
        return self.atoms.index(item)

    def append(self, atom):
        self.atoms.append(atom)

    def extend(self, other):
        self.atoms.extend([_ for _ in other])

    @classmethod
    def from_fileobject(cls, file):
        atoms = []
        current_model = None
        for line in file:
            if line.startswith('MODEL'):
                current_model = int(line.split()[1])
            elif line.startswith('ENDMDL'):
                current_model = None
            else:
                try:
                    atom = Atom.from_string(line)
                    atom.model = current_model
                    atoms.append(atom)
                except Atom.InvalidAtomString:
                    pass
        return cls(atoms)

    @classmethod
    def from_file(cls, filename):
        with open(filename) as f:
            return cls.from_fileobject(f)

    @classmethod
    def from_code(cls, pdb_code):
        with PdbFile(pdb_code) as f:
            return cls.from_fileobject(f)

    @cached_property
    def models(self):
        models = OrderedDict()
        for atom in self:
            key = atom.model
            if key not in models:
                models[key] = Atoms()
            models[key].append(atom)
        return models

    @cached_property
    def chains(self):
        chains = OrderedDict()
        for atom in self:
            key = atom.chain
            if key not in chains:
                chains[key] = Atoms()
            chains[key].append(atom)
        return chains

    @cached_property
    def residues(self):
        residues = OrderedDict()
        for atom in self:
            key = atom.resid
            if key not in residues:
                residues[key] = Atoms()
            residues[key].append(atom)
        return residues

    @cached_property
    def models_count(self):
        return len(self.models)

    @cached_property
    def chains_count(self):
        return len(self.chains)

    @cached_property
    def residues_count(self):
        return len(self.residues)

    @cached_property
    def models_list(self):
        return list(self.models.values())

    @cached_property
    def chains_list(self):
        return list(self.chains.values())

    @cached_property
    def residues_list(self):
        return list(self.residues.values())

    @property
    def pdb(self):
        if len(self.models) > 1:
            return ''.join([f'MODEL{model:9d}\n{str(atoms)}\nENDMDL\n' for model, atoms in self.models.items()])
        else:
            return str(self)

    @property
    def numpy(self):
        return np.concatenate([atom.R.numpy.reshape(1, 3) for atom in self])

    @numpy.setter
    def numpy(self, coords):
        for atom, coord in zip(self, coords):
            atom.R = Vector(coord)

    def move(self, vector):
        for atom in self:
            atom.R += vector
        return self

    @property
    def cent_of_mass(self):
        return Vector(np.average(self.numpy, 0))

    @cent_of_mass.setter
    def cent_of_mass(self, vector):
        self.move(vector - self.cent_of_mass)

    def center_at_origin(self):
        self.cent_of_mass = Vector()
        return self

    def rotate(self, matrix, is_centered=False):
        coord = self.numpy
        if not is_centered:
            com = np.average(coord, 0)
            coord = np.dot(coord - com, matrix) + com
        else:
            coord = np.dot(coord, matrix)
        self.numpy = coord
        return self

    def select(self, selection):
        if not isinstance(selection, Selection):
            selection = Selection(selection)
        return Atoms([atom for atom in self if selection.match(atom)])

    def drop(self, selection):
        if not isinstance(selection, Selection):
            selection = Selection(selection)
        return Atoms([atom for atom in self if not selection.match(atom)])

    def partition(self, selection):
        if not isinstance(selection, Selection):
            selection = Selection(selection)
        sele, drop = [], []
        for atom in self:
            sele.append(atom) if selection.match(atom) else drop.append(atom)
        return Atoms(sele), Atoms(drop)

    def update_ss(self):
        dssp = DsspFile.from_pdb(self.pdb).data
        for atom in self:
            atom.ss = dssp.get(atom.resid_id, 'C')

    def generate_ca_restraints(self, mode, gap, min_dist, max_dist):
        ca = self.select('name CA')
        restr = []
        for num, atom1 in enumerate(ca):
            ss1 = atom1.ss not in 'HE'  # True for 'C' and 'T'
            if mode == 'ss2' and ss1:
                continue
            for atom2 in ca[num + gap:]:
                ss2 = atom2.ss not in 'HE'  # True for 'C' and 'T'
                if (mode == 'ss2' and ss2) or (mode == 'ss1' and ss1 and ss2):
                    continue
                dist = (atom1.R - atom2.R).length
                if min_dist < dist < max_dist:
                    restr.append((
                      atom1.resid_id, atom2.resid_id, dist
                    ))
        return restr


class Trajectory:

    """Class to hold multiple structures of the same collection of atoms"""

    def __init__(self, template, coordinates):
        self.template = template
        self.coordinates = coordinates

    @property
    def models(self):
        return len(self.coordinates)

    @classmethod
    def from_atoms(cls, atoms):
        models = atoms.models_list
        template = models[0]
        coordinates = atoms.numpy.reshape(-1, len(template), 3)
        return cls(template, coordinates)

    def select(self, selection):
        template = self.template.select(selection)
        return Trajectory(template, self.coordinates[:, [self.template.index(_) for _ in template], :])

    @property
    def atoms(self):
        atoms = Atoms()
        for i in range(self.coordinates.shape[0]):
            model = deepcopy(self.template)
            for atom in model:
                atom.model = i + 1
            model.numpy = self.coordinates[i]
            atoms.extend(model)
        return atoms

    @property
    def pdb(self):
        pdb = []
        for model, coordinates in enumerate(self.coordinates, 1):
            self.template.numpy = coordinates
            pdb.append(f'MODEL{model:9d}\n{self.template.pdb}\nENDMDL\n')
        return ''.join(pdb)

    # structural fit
    def fit_to(self, atoms, selection=None):
        target = atoms.numpy
        target_com = np.average(target, axis=0)
        target = target - target_com
        tra = self.select(selection).coordinates if selection else self.coordinates
        for i in range(self.models):
            query = tra[i]
            query_com = np.average(query, axis=0)
            query = query - query_com
            self.coordinates[i] = np.dot(
                self.coordinates[i] - query_com,
                kabsch(target, query, concentric=True)
            ) + target_com

        return self

    def __getitem__(self, item):
        atoms = deepcopy(self.template)
        atoms.numpy = self.coordinates[item]
        return atoms
