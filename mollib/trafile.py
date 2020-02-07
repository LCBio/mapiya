import numpy as np
import io
import tarfile
import lzma
import pickle
from collections import defaultdict
from cached_property import cached_property

from mollib.atom import Atom, Atoms, Trajectory


class Header:

    """Frame header in .tra file"""

    def __init__(self, replica=0, model=0, chains=0, temperature=0., energy=None):
        self.replica = replica
        self.model = model
        self.chains = chains
        self.temperature = temperature
        self.energy = energy

    def __str__(self):
        return f'Replica: {self.replica:d} Model: {self.model:d}'

    @classmethod
    def from_line(cls, line):
        words = line.split()
        return Header(
            replica=int(words[-1]),
            model=int(words[0]),
            chains=len(words) - 4,
            temperature=float(words[-2]),
            energy=np.array(words[2:-2], dtype=float).reshape(1, -1)
        )

    def merge(self, other):
        if self.replica == other.replica and self.model == other.model:
            self.energy = np.concatenate([self.energy, other.energy])
        else:
            raise ValueError('Cannot merge headers')

    @property
    def compressed(self):
        _data = [self.temperature]
        for i in range(self.chains):
            for j in range(i, self.chains):
                _data.append(self.energy[i][j])
        return np.array(_data, dtype=np.float32)


class Trafile:

    """CABS trajectory file"""

    LATTICE_UNIT = 0.61

    def __init__(self, template, coordinates, headers=None):
        self.template = template  # Atoms()
        self.coordinates = coordinates  # np.array(shape=(replicas, frames, atoms, 3), dtype=np.int16)
        self.headers = headers  # np.array(shape=(replicas, frames, len(header.compressed)), dtype=np.float32)

    def __getitem__(self, item):
        return Trajectory(self.template, self.LATTICE_UNIT * self.coordinates[item])

    @property
    def replicas(self):
        return self.coordinates.shape[0]

    @property
    def frames(self):
        return self.coordinates.shape[1]

    @cached_property
    def trajectories(self):
        return [self[_] for _ in range(self.replicas)]

    @staticmethod
    def read_seq(fileobject):
        fileobject = io.TextIOWrapper(fileobject, encoding='utf-8')
        atoms = Atoms()
        for i, line in enumerate(fileobject, 1):
            atoms.append(Atom(
                serial=i,
                resnum=int(line[:5]),
                icode=line[5],
                altloc=line[7],
                resname=line[8:11],
                chain=line[12],
                occ=float(line[13:16]),
                bfac=float(line[16:22])
            ))
        return atoms

    @staticmethod
    def read_tra(fileobject):

        fileobject = io.TextIOWrapper(fileobject, encoding='utf-8')
        replicas = defaultdict(list)
        header = Header.from_line(next(fileobject))
        coordinates = []
        current_coordinates = []

        for line in fileobject:
            if '.' in line:
                current_header = Header.from_line(line)
                coordinates.extend(' '.join(current_coordinates).split()[3:-3])
                current_coordinates = []
                try:
                    header.merge(current_header)
                except ValueError:
                    replicas[header.replica].append((
                        header.compressed,
                        np.array(coordinates, dtype=np.int16).reshape(-1, 3)
                    ))
                    header = current_header
                    coordinates = []
            else:
                current_coordinates.append(line)
        else:
            coordinates.extend(' '.join(current_coordinates).split()[3:-3])
            replicas[header.replica].append((
                header.compressed,
                np.array(coordinates, dtype=np.int16).reshape(-1, 3)
            ))

        return replicas

    @classmethod
    def from_tra_seq(cls, template, replicas):
        coordinates = None
        headers = None

        for num in sorted(replicas):
            frames = replicas[num]
            current_headers = np.concatenate([frame[0] for frame in frames])
            current_coords = np.concatenate([frame[1] for frame in frames])
            headers = current_headers if headers is None else np.concatenate([headers, current_headers])
            coordinates = current_coords if coordinates is None else np.concatenate([coordinates, current_coords])

        coordinates = coordinates.reshape(len(replicas), -1, len(template), 3)
        headers = headers.reshape(len(replicas), coordinates.shape[1], -1)

        return cls(template, coordinates, headers)

    @classmethod
    def from_files(cls, tra_file, seq_file):
        return cls.from_tra_seq(cls.read_seq(seq_file), cls.read_tra(tra_file))

    @classmethod
    def from_filenames(cls, tra_filename='TRAF', seq_filename='SEQ'):
        with open(tra_filename) as _tra, open(seq_filename) as _seq:
            return cls.from_files(_tra, _seq)

    @classmethod
    def load(cls, filename):
        try:
            with lzma.open(filename) as xz:
                return pickle.loads(xz.read())

        except lzma.LZMAError:
            with tarfile.open(filename, 'r:gz') as tar:
                return cls.from_files(tar.extractfile('TRAF'), tar.extractfile('SEQ'))

    def save(self, filename):
        with open(filename, 'wb') as cbs:
            cbs.write(lzma.compress(pickle.dumps(self)))


class Energy:

    def __init__(self, trafile):

        self.temperatures = trafile.headers[:, :, 0]
        self.chains = list(trafile.template.chains.keys())
        chains = len(self.chains)
        replicas = self.temperatures.shape[0]
        frames = self.temperatures.shape[1]
        self.energies = np.zeros(dtype=float, shape=(replicas, frames, chains, chains))
        energies = trafile.headers[:, :, 1:]

        for ii in range(replicas):
            for jj in range(frames):
                k = iter(energies[ii][jj])
                for i in range(chains):
                    for j in range(i, chains):
                        self.energies[ii][jj][i][j] = self.energies[ii][jj][j][i] = next(k)
