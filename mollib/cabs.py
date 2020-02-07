"""
Module for handling CABS model representation of proteins
"""

import numpy as np
from cached_property import cached_property
import os
from mollib.trafile import Atoms
from copy import deepcopy
import logging


class CabsLattice:

    MOLLIB_CACHE = os.path.join(os.path.expanduser('~'), '.mollib')
    LATTICE_UNIT = 0.61

    AA_NAME = [
        'GLY', 'ALA', 'SER', 'CYS', 'VAL',
        'THR', 'ILE', 'PRO', 'MET', 'ASP',
        'ASN', 'LEU', 'LYS', 'GLU', 'GLN',
        'ARG', 'HIS', 'PHE', 'TYR', 'TRP'
    ]

    SIDECENT = np.array([
        0.0, -0.111, -0.111, 0.0, -0.111, -0.111,
        0.253, -1.133, 0.985, 0.119, -0.763, 1.312,
        0.121, -1.476, 1.186, 0.223, -1.042, 1.571,
        -0.139, -1.265, 1.619, 0.019, -0.813, 1.897,
        0.264, -1.194, 1.531, 0.077, -0.631, 1.854,
        0.075, -1.341, 1.398, 0.051, -0.909, 1.712,
        0.094, -1.416, 1.836, -0.105, -0.659, 2.219,
        -0.751, -1.643, 0.467, -1.016, -1.228, 0.977,
        -0.04, -1.446, 2.587, 0.072, -0.81, 2.883,
        -0.287, -1.451, 1.989, 0.396, -0.798, 2.313,
        -0.402, -1.237, 2.111, 0.132, -0.863, 2.328,
        -0.069, -1.247, 2.292, 0.002, -0.462, 2.579,
        0.032, -1.835, 2.989, 0.002, -0.882, 3.405,
        -0.028, -1.774, 2.546, 0.096, -0.923, 3.016,
        -0.095, -1.674, 2.612, 0.047, -0.886, 2.991,
        -0.057, -2.522, 3.639, -0.057, -1.21, 3.986,
        -0.301, -1.405, 2.801, -0.207, -0.879, 3.019,
        0.151, -1.256, 3.161, -0.448, -0.791, 3.286,
        0.308, -1.387, 3.492, -0.618, -0.799, 3.634,
        0.558, -1.694, 3.433, -0.06, -0.574, 3.834
    ]).reshape(20, 2, 3)

    def __init__(self):
        os.makedirs(self.MOLLIB_CACHE, exist_ok=True)

    @cached_property
    def vectors(self):
        return np.array([
            [i, j, k]
            for i in range(-7, 8)
            for j in range(-7, 8)
            for k in range(-7, 8)
            if 28 < i * i + j * j + k * k < 50
        ], dtype=np.int16)

    @cached_property
    def vectors_map(self):
        return {(v[0], v[1], v[2]): i for i, v in enumerate(self.vectors)}

    @cached_property
    def sg(self):
        sg_path = os.path.join(self.MOLLIB_CACHE, 'sg.npy')
        try:
            sg = np.load(sg_path)
            logging.debug(f'SC config loaded from: "{sg_path}".')
            return sg
        except FileNotFoundError:
            vcount = len(self.vectors)
            sg = np.zeros(shape=(vcount, vcount, len(self.AA_NAME), 3), dtype=np.float16)

            logging.debug(f'Generating SC config. This will take some time.')

            for i, vi in enumerate(self.vectors):
                if (i + 1) % 80 == 0:
                    logging.debug(f'SC config: {(i + 1)/ 8.:.0f}% complete')
                for j, vj in enumerate(self.vectors):
                    vsum = vi + vj
                    conf = np.dot(vsum, vsum)
                    if conf < 45 or conf > 145:
                        continue
                    vcross = np.cross(vi, vj)
                    cross = np.dot(vcross, vcross)
                    if cross == 0:
                        continue
                    vsum = vsum / np.sqrt(conf)
                    vdiff = vi - vj
                    vdiff = vdiff / np.sqrt(np.dot(vdiff, vdiff))
                    vcross = vcross / np.sqrt(cross)

                    base = np.stack([vsum, vcross, vdiff]).T

                    fb = 0.0 if conf < 75 else 1.0 if conf > 110 else (conf - 75.) / 35.
                    fa = 1 - fb

                    for k in range(len(self.AA_NAME)):
                        sg[i][j][k] = np.dot(base, fa * self.SIDECENT[k][0] + fb * self.SIDECENT[k][1])

            logging.debug(f'SC config saved to: "{sg_path}"')
            np.save(sg_path, sg)
            return sg

    @staticmethod
    def rebuild_template(template):
        logging.debug(f'Rebuilding template.')
        new_template = Atoms()
        for index, atom in enumerate(template):
            ca = deepcopy(atom)
            ca.serial = 3 * index + 1
            new_template.append(ca)
            cb = deepcopy(ca)
            cb.name = 'CB'
            cb.serial = 3 * index + 2
            new_template.append(cb)
            sg = deepcopy(ca)
            sg.name = 'SG'
            sg.serial = 3 * index + 3
            new_template.append(sg)
        return new_template

    def parse_seq(self, template):
        logging.debug(f'Mapping protein sequence')
        return [
            [self.AA_NAME.index(atom.resname) for atom in chain]
            for chain in template.chains_list
        ]

    def rebuild_chain(self, seq, chain):

        ca_vectors = [
            self.vectors_map[tuple(chain[i] - chain[i - 1])] if i else None
            for i in range(len(seq))
        ]

        ca_vectors[0] = ca_vectors[2]
        ca_vectors.append(ca_vectors[-2])
        ca = chain * self.LATTICE_UNIT

        return np.concatenate([
            np.stack([
                ca[i],
                ca[i] + self.sg[ca_vectors[i], ca_vectors[i + 1], 1],
                ca[i] + self.sg[ca_vectors[i], ca_vectors[i + 1], seq[i]]
            ]) for i in range(len(seq))
        ])

    def rebuild_frame(self, seqs, frame):
        coordinates = []
        start = 0
        for seq in seqs:
            end = start + len(seq)
            coordinates.append(self.rebuild_chain(seq, frame[start:end, :]))
            start = end
        return np.concatenate(coordinates)

    def rebuild_replica(self, seqs, replica, index, nreps):
        logging.debug(f'Rebuilding replica {index:d}/{nreps:d}')
        return np.stack([self.rebuild_frame(seqs, frame) for frame in replica])

    def rebuild_trafile(self, trafile):
        seqs = self.parse_seq(trafile.template)
        return np.stack([
            self.rebuild_replica(seqs, replica, index, trafile.replicas)
            for index, replica in enumerate(trafile.coordinates, 1)
        ])
