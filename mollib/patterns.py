import math


def check_seq(seq):

    if type(seq) == str:
      seq = list(seq)
    if len(seq[0]) == 1:
      seq = [AA_CODES[i] for i in seq]
    return seq

def calc_patterns(seq):

    seq = check_seq(seq)
    data_1D = {}
    data_1D['composition'] = list(AA_ATTRIBUTES[i][6] for i in seq)
    data_1D['hydropathy'] = list(round((AA_ATTRIBUTES[i][5]+4.5)/9.0,2) for i in seq)
    s_len = len(seq)

    for z in PATTERNS.keys():
        data_1D[z] = ['0']*s_len
    for n, j in enumerate(seq):
        for z in ['hydrophobic', 'amphipatic', 'hydrophilic', 'polar', 'nonpolar', 'aromatic', 'π-bond', 'H-Bond donor', 'H-Bond acceptor']:
            if j in PATTERNS[z]:
                data_1D[z][n] = '0.7'
        for z in ['charged', 'sulfur']:
            if j in PATTERNS[z][0]:
                data_1D[z][n] = 0.5
            elif j in PATTERNS[z][1]:
                data_1D[z][n] = 0.8
    return data_1D


def calc_entropy(seq, shift=6):

    seq = check_seq(seq)
    s_len = len(seq)
    entropy = [0]*s_len

    for n, j in enumerate(seq):
        if n <= s_len - shift:
            frag = seq[n:n+shift]
            S = 0
            for kk in AA_ATTRIBUTES.keys():
                gg = frag.count(kk)/shift
                if gg > 0:
                    S += gg*math.log2(gg)
            for z in range(n, n+shift):
              entropy[z] += (S*(-1))/shift
    return ["%.2f" % i for i in entropy]


PATTERNS = {
    'hydrophobic'     : ['ALA', 'GLY', 'LEU', 'ILE', 'VAL', 'PRO', 'PHE'],
    'amphipatic'      : ['TRP', 'TYR', 'MET', 'LYS'],
    'hydrophilic'     : ['ARG', 'ASN', 'ASP', 'GLN', 'GLU', 'HIS', 'SER', 'THR', 'CYS'],
    'charged'         : [['LYS', 'ARG', 'HIS'], ['GLU', 'ASP']],
    'polar'           : ['CYS', 'MET', 'SER', 'THR', 'TYR', 'GLN', 'ASN'],
    'nonpolar'        : ['ALA', 'GLY', 'ILE', 'LEU', 'VAL', 'PHE', 'PRO', 'TRP'],
    'aromatic'        : ['PHE', 'TYR', 'TRP', 'HIS'],
    'π-bond'          : ['ARG', 'ASN', 'ASP', 'GLN', 'GLU', 'GLY'],
    'sulfur'          : [['MET'], ['CYS']],
    'H-Bond donor'    : ['ARG', 'ASN', 'GLN', 'HIS', 'LYS', 'SER', 'THR', 'TRP', 'TYR'],
    'H-Bond acceptor' : ['ASN', 'ASP', 'GLN', 'GLU', 'HIS', 'SER', 'THR', 'TYR']
}

AA_CODES = {
    'A': 'ALA', 'C': 'CYS', 'D': 'ASP', 'E': 'GLU', 'F': 'PHE',
    'G': 'GLY', 'H': 'HIS', 'I': 'ILE', 'K': 'LYS', 'L': 'LEU',
    'M': 'MET', 'N': 'ASN', 'P': 'PRO', 'Q': 'GLN', 'R': 'ARG',
    'S': 'SER', 'T': 'THR', 'V': 'VAL', 'W': 'TRP', 'Y': 'TYR'
}

# id - mass - frequency - charge - aromatic - KD_hydropathy - color
AA_ATTRIBUTES = {
    'ALA': [ 0,  89.094, 8.76,  0.0, 0.0,  1.8, 0.75],
    'CYS': [ 1, 121.154, 1.38,  0.0, 0.0,  2.5, 0.90],
    'ASP': [ 2, 133.104, 5.49, -1.0, 0.0, -3.5, 0.25],
    'GLU': [ 3, 147.131, 6.32, -1.0, 0.0, -3.5, 0.30],
    'PHE': [ 4, 165.192, 3.87,  0.0, 1.0,  2.8, 0.05],
    'GLY': [ 5,  75.067, 7.03,  0.0, 0.0, -0.4, 0.80],
    'HIS': [ 6, 155.156, 2.26,  0.5, 1.0, -3.2, 0.45],
    'ILE': [ 7, 131.175, 5.49,  0.0, 0.0,  4.5, 0.65],
    'LYS': [ 8, 146.189, 5.19,  1.0, 0.0, -3.9, 0.50],
    'LEU': [ 9, 131.175, 9.68,  0.0, 0.0,  3.8, 0.60],
    'MET': [10, 149.208, 2.32,  0.0, 0.0,  1.9, 0.85],
    'ASN': [11, 132.119, 3.93,  0.0, 0.0, -3.5, 0.15],
    'PRO': [12, 115.132, 5.02,  0.0, 0.0, -1.6, 0.95],
    'GLN': [13, 146.146, 3.90,  0.0, 0.0, -3.5, 0.20],
    'ARG': [14, 174.203, 5.78,  1.0, 0.0, -4.5, 0.55],
    'SER': [15, 105.093, 7.14,  0.0, 0.0, -0.8, 0.35],
    'THR': [16, 119.119, 5.53,  0.0, 0.0, -0.7, 0.40],
    'VAL': [17, 117.148, 6.73,  0.0, 0.0,  4.2, 0.70],
    'TRP': [18, 204.228, 1.25,  0.0, 1.0, -0.9, 0.00],
    'TYR': [19, 181.191, 2.91,  0.0, 1.0, -1.3, 0.10]
}

