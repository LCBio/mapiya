# -*- coding: utf-8 -*-
import os
import subprocess
import tempfile

import openmm as mm
import pandas as pd
import simtk.unit as unit
from openmm.app import PDBFile
from pdbfixer import PDBFixer

# const/default variables
SS = {'B': 'Bridge', 'C': 'Coil', 'E': 'Strand', 'G': '310Helix', 'H': 'AlphaHelix', 'T': 'Turn'}


def fix_pdb_with_pdbfixer(filename, chains='all', params=None):
    """Fix PDB using pdbfixer library. Function called by "run_external_software" defined below.

       filename - full length path to input PDB
       chains - keep chains: 'all' or list of chain ids, e.g. ['A', 'B', 'C']
       params - dict of key-value options required by pdbfixer and APBS, by default "opts" dictionary
    """
    prefix = filename.split('/')[-1].split('.')[0]
    log = []

    fixer = PDBFixer(filename=filename)

    # Remove chains
    if chains != 'all':
        remove_ch = [chain.id for chain in fixer.topology.chains() if chain.id not in chains]
        fixer.removeChains(chainIds=remove_ch)
        log.append(
            f'INFO: removed chains: {remove_ch}\n      kept chains: {[chain.id for chain in fixer.topology.chains()]}'
        )
    else:
        log.append(f'INFO: kept all chains: {[chain.id for chain in fixer.topology.chains()]}')

    # Remove heterogens
    if params['keep_heterogens'] != 'all':
        if params['keep_heterogens'] == 'water':
            fixer.removeHeterogens(True)
            log.append("INFO: removed heterogens except water.")
        elif params['keep_heterogens'] == 'none':
            fixer.removeHeterogens(False)
            log.append("INFO: removed all heterogens including water.")
        else:
            log.append("INFO: kept all heterogens including water.")

    # Apply mutations
    if params['apply_mutations']:
        mutations = {}
        for i in params['specify_mutations'].strip().split(','):  # e.g, 'VAL-3-ILE:A,ILE-7-VAL:A'
            mutant = i.split(':')
            if not mutant[1] in mutations.keys():
                mutations[mutant[1]] = [mutant[0]]
            else:
                mutations[mutant[1]].append(mutant[0])
        for chain in mutations:
            try:
                fixer.applyMutations(mutations[chain], chain)
                log.append(f"INFO: applied mutations in chain {chain} : {mutations[chain]}")
            except:
                log.append(
                    f"ERROR: mutation in chain {chain} is not possible because at least one residue "
                    f"on your list: {mutations[chain]} does not exist."
                )
    else:
        log.append("INFO: applied none mutation.")

    # Replace nonstandard residues
    if params['replace_non_standard']:
        fixer.findNonstandardResidues()
        log.append("INFO: replaced nonstandard residues: " + str(fixer.nonstandardResidues))
        fixer.replaceNonstandardResidues()
    else:
        fixer.findNonstandardResidues()
        log.append("INFO: nonstandard residues were NOT replaced: " + str(fixer.nonstandardResidues))

    # Rebuild missing residues, the residues actually get added when you call addMissingAtoms()
    n = 0
    if params['add_residues'] != 'none':
        fixer.findMissingResidues()
        if len(fixer.missingResidues):
            s = '\n'
        else:
            s = ' []'
        for key in fixer.missingResidues:
            s += "\tchain: " + list(fixer.topology.chains())[key[0] - 1].id + " at position: " + str(
                key[1]) + ": " + str(fixer.missingResidues[key]) + "\n"
        log.append("INFO: missing residues are: " + s)
        keys = list(fixer.missingResidues)
        chains = list(fixer.topology.chains())
        for key in keys:
            chain = chains[key[0]]
            if params['add_residues'] == 'internal':
                if key[1] == 0 or key[1] == len(list(chain.residues())):
                    del fixer.missingResidues[key]
            elif params['add_residues'] == 'terminal':
                if key[1] != 0 or key[1] != len(list(chain.residues())):
                    del fixer.missingResidues[key]
        keys = list(fixer.missingResidues)
        for key in keys:
            if len(fixer.missingResidues[key]) > int(params['max_loop_length']):
                del fixer.missingResidues[key]
        s = '\n'
        for key in fixer.missingResidues:
            n += len(fixer.missingResidues[key])
            s += "\tchain: " + list(fixer.topology.chains())[key[0] - 1].id + " at position: " + str(
                key[1]) + ": " + str(fixer.missingResidues[key]) + "\n"
    else:
        fixer.missingResidues = {}
        s = ' []'
    log.append(
        f"INFO: rebuilt {params['add_residues']} ({n}) residues in loops shorter than {params['max_loop_length']}: {s}"
    )

    # Retrieve missing atoms.
    if params['add_atoms'] != 'none' and params['add_atoms'] != 'hydrogen':
        fixer.findMissingAtoms()
        if params['add_atoms'] == 'standard':
            fixer.missingTerminals = {}
        elif params['add_atoms'] == 'terminal':
            fixer.findMissingAtoms = {}
        if len(fixer.missingAtoms):
            s = '\n'
            for key in fixer.missingAtoms:
                for at in fixer.missingAtoms[key]:
                    s += "\tchain: " + key.chain.id + " in residue: " + key.name + "-" + key.id + ": " \
                         + at.name + "-" + at.id + "\n"
        else:
            s = ' []'
        log.append("INFO: added missing standard atoms: " + s)
        if len(fixer.missingTerminals):
            s = '\n'
            for key in fixer.missingTerminals:
                s += "\tchain: " + key.chain.id + " in residue: " + key.name + "-" + key.id + ": " + \
                     fixer.missingTerminals[key][0] + "\n"
        else:
            s = ' []'
        log.append("INFO: added missing terminal atoms: " + s)
        fixer.addMissingAtoms()
    elif params['add_atoms'] == 'none':
        log.append("INFO: no atoms added")

    if params['add_atoms'] == 'hydrogen' or params['add_atoms'] == 'all':
        fixer.addMissingHydrogens(params['protonation_ph'])
        log.append("INFO: added missing hydrogens for state protonated at pH="+str(params['protonation_ph']))

    PDBFile.writeFile(fixer.topology, fixer.positions, open(prefix+'_fixed.pdb', 'w'))

    # Add a water box
    if params['add_environment'] != 'none':
        ions = [params['positive_ion'], params['negative_ion'], params['ionic_strength']]
        if params['add_environment'] == 'solvent':
            boxSize = fixer.topology.getUnitCellDimensions()
            if params['water_box'] == 'unitcell':
                boxSize = boxSize
            elif params['water_box'] == 'maxsize':
                maxSize = max(
                    max((pos[i] for pos in fixer.positions)) - min((pos[i] for pos in fixer.positions))
                    for i in range(3)
                )
                boxSize = maxSize*mm.Vec3(1, 1, 1)
            elif params['water_box'] == 'custom':
                bs = [float(i) for i in params['box_dimensions'].split(',')]
                boxSize = mm.Vec3(bs[0], bs[1], bs[2]) * unit.nanometers
            try:
                fixer.addSolvent(
                    boxSize, positiveIon=ions[0], negativeIon=ions[1], ionicStrength=float(ions[2]) * unit.molar
                )
                log.append(
                    "INFO: added solvent: water box dimensions: " + str(boxSize) + "; ion(+)=" + ions[0] + "; ion(-)=" +
                    ions[1] + "; ionic strength: " + str(ions[2]) + " molar"
                )
                PDBFile.writeFile(fixer.topology, fixer.positions, open(prefix+'_fixed_envir.pdb', 'w'))
            except Exception as e:
                log.append(f"INFO: adding solvent failed due to an error: {e}")

        elif params['add_environment'] == 'membrane':
            mem = [params['lipid_type']]
            mem.extend(params['membrane_position'].split(','))
            try:
                fixer.addMembrane(lipidType=mem[0], membraneCenterZ=float(mem[1]), minimumPadding=float(mem[2]),
                                  positiveIon=ions[0], negativeIon=ions[1], ionicStrength=float(ions[2]) * unit.molar)
                log.append("INFO: added membrane: lipid type: " + mem[0] + "; ion(+)=" + ions[0] + "; ion(-)=" + ions[
                    1] + "; ionic strength: " + str(ions[2]) + " molar")
                PDBFile.writeFile(fixer.topology, fixer.positions, open(prefix+'_fixed_envir.pdb', 'w'))
            except Exception as e:
                log.append(f"INFO: adding membrane failed due to an error: {e}")
    else:
        log.append("INFO: no solvent or membrane added")
    return log


#  ***** RUN EXTERNAL SOFTWARE *****#
def run_external_software(filename, chains='all', params=None):
    """Run external software to get data used by mapserver.

       filename - full path to PDB file (most probably in ~/media/)
       chains - 'all' or list of chains ids to be kept for analysis
       params - dict of key-value options required by pdbfixer and APBS
    """

    prefix = filename.split('/')[-1].split('.')[0]  # PDB code + model index, e.g., prefix = 2GB1_1 when filename = <path_to_media_user_project>/2GB1_1.pdb
    dirpath = os.path.dirname(filename)			# derived <path_to_media_user_project>

    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)

        pdbfixer_log = fix_pdb_with_pdbfixer(filename, chains, params)		### run PDBfixer: save filename_fixed.pdb (always) and filename_fixed_envir.pdb (if requested)
        os.system('stride -h -f'+prefix+'.stride '+prefix+'_fixed.pdb')		### run STRIDE to get: secondary structure, solvent accessibility, ramachandran angles
        os.system(f"pdb2pqr --ff=PARSE --apbs-input {prefix}.in --titration-state-method=propka "
                  f"--with-ph={params['protonation_ph']} {prefix}_fixed.pdb {prefix}.pqr 2> apbs.out")
        os.system('apbs --output-file=apbs.config '+prefix+'.in >> apbs.out')	### run APBS to get electrostatics
        p = subprocess.Popen(['whereis', 'edhb'], stdout=subprocess.PIPE)	### (!) make sure that the venv is activated: 'conda activate venv'
        venvdir = str(p.stdout.read().decode('ascii')).strip().split()[1].strip().replace('edhb','')
        os.system('ln -s '+venvdir+'main_input ./')				### (!) required in the current path for edhb
        os.system('ln -s '+venvdir+'init.txt ./')				### (!) required in the current path for edhb
        os.system('edhb '+prefix+'_fixed.pdb -c -a -B -R')			### run EDHB to get hydrogen bonds
        ### save important outputs in ~/media/ dir
        os.system('cp '+prefix+'_fixed.pdb '+prefix+'_fixed_envir.pdb '+prefix+'.pqr '+prefix+'.pqr.dx '+dirpath)
        os.system(f'cp apbs.config {dirpath}/{prefix}.apbs')

#        print(os.listdir(tmp_dir))

        ### parse STRIDE outputs
        ss_elements = {}
        structural_data = pd.DataFrame(columns = ['chain','residues','secondary_structure','solvent_accessibility','phi','psi','mainHB_acceptor'])
        path_to_file = os.getcwd()+'/'+prefix+'.stride'
        if os.path.exists(path_to_file):
            with open(path_to_file,'r') as f:
                for row in f:
                    if row.startswith('LOC'):
                        element = row[5:17].strip()
                        if not element in ss_elements:
                            ss_elements[element] = []
                        ss_elements[element].append(row[18:21].strip()+':'+row[22:27].strip()+'_'+row[28]+'-'+row[35:38].strip()+':'+row[41:45].strip()+'_'+row[46])
                    elif row.startswith('ASG'):
                        structural_data.loc[len(structural_data.index)] = [row[9], row[5:8].strip()+':'+row[11:15].strip(), row[24:25].strip(), row[64:69].strip(), row[42:49].strip(), row[52:59].strip(), {}]
                    elif row.startswith('DNR'):
                        acc = row[25:28].strip()+':'+row[31:35].strip()+'_'+row[29]
                        donor = row[5:8].strip()+':'+row[11:15].strip()
                        value = [row[41:45].strip(), row[46:52].strip(), row[53:59].strip(), row[60:66].strip(), row[67:73]]	#[0] N..0 distance; [1] N..O=C angle; [2] O..N-C angle; [3] A1 (Angle between the planes of donor complex and O..N-C); [4] A2 (angle between the planes of acceptor complex and N..O=C)
                        structural_data.loc[(structural_data['chain'] == row[9]) & (structural_data['residues'] == donor)]['mainHB_acceptor'].values[0][acc] = value

        ### parse EDHB outputs
        HB = pd.DataFrame(columns = ['chains','donor','acceptor','proton','acc_atom','ids','type','bond','length','angle','intraHB','bifurcation'])
        path_to_edhb = os.getcwd()+'/'+prefix+'_fixed.xls'
        path_to_fixer = os.getcwd()+'/'+prefix+'_fixed.pdb'
        if os.path.exists(path_to_edhb) and os.path.exists(path_to_fixer):
            edhb = pd.read_excel(path_to_edhb)
            inds = pd.DataFrame(columns = ['chain','residue','atom', 'ix'])
            with open(path_to_fixer,'r') as f:
                for row in f:
                    if row.startswith('ATOM'):
                        inds.loc[len(inds.index)] = [row[21], row[17:20].strip()+':'+row[22:26].strip(), row[11:16].strip(), row[4:11].strip()]
        for index, row in edhb.iterrows():
            ids = row['atomIDs'].split('-')
            proton = inds[inds.ix == ids[1]]
            acceptor = inds[inds.ix == ids[0]]
            if len(proton) and len(acceptor):		# remove HB with water molecules
                backbone = ['N', 'H', 'H2', 'H3', 'CA', 'HA', 'C', 'O']
                chains = proton['chain'].values[0]+':'+acceptor['chain'].values[0]
                at_d = proton['atom'].values[0]
                at_a = acceptor['atom'].values[0]
                ix_d = proton['ix'].values[0]
                ix_a = acceptor['ix'].values[0]
                td = ta = 's'
                if at_d in backbone:
                    td = 'b'
                if at_a in backbone:
                    ta = 'b'
                HB.loc[len(HB.index)] = [chains, proton['residue'].values[0], acceptor['residue'].values[0], at_d, at_a, ix_d+':'+ix_a, td+ta, row['Bond'], row['HB length'], row['HB Angle'], row['Intra-HB'], row['Bifurcation type']]

    return pdbfixer_log, ss_elements, structural_data, HB

