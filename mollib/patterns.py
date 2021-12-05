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
                data_1D[z][n] = 0.7
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


def calc_struct(seq, struct):

    resids = struct.residues.tolist()
    ss_t = struct['secondary_structure'].tolist()
    sa_t = struct['solvent_accessibility'].tolist()
    ss = []
    sa = []
    if len(seq) != len(resids):
        for i in seq:
            if i in resids:
                k = resids.index(i)
                ss.append(ss_t[k])
                sa.append(sa_t[k])
            else:
                ss.append('C')
                sa.append(AA_ATTRIBUTES[i.split(':')[0]][7][0])
    else:
        ss = ss_t
        sa = sa_t
    sec_struct = [SS_CODES['8-letter'][i.upper()] for i in ss]
    sasa = [round(sa[n]/AA_ATTRIBUTES[i.split(':')[0]][7][0], 2) for n, i in enumerate(seq)]
    return sec_struct, sasa


def calc_contact_nature(res1, res2):

    desc = 'YES<br>possible interaction forces:<br>'
    key = sorted([AA_ATTRIBUTES[res1][0], AA_ATTRIBUTES[res2][0]])
    for i in INTERACTION[str(key[0])+':'+str(key[1])]:
        desc += DESCRIPTORS[i]
    return desc


def filter_contact_by_nature(res1, res2, feature):

    if feature == 'hydropathy':
        if res1 in PATTERNS['hydrophilic']:
            if res2 in PATTERNS['hydrophilic']:
                return 0.1
            elif res2 in PATTERNS['amphipatic']:
                return 0.3
        elif res1 in PATTERNS['amphipatic']:
            if res2 in PATTERNS['hydrophilic']:
                return 0.3
            elif res2 in PATTERNS['amphipatic']:
                return 0.5
            elif res2 in PATTERNS['hydrophobic']:
                return 0.7
        elif res1 in PATTERNS['hydrophobic']:
            if res2 in PATTERNS['amphipatic']:
                return 0.7
            elif res2 in PATTERNS['hydrophobic']:
                return 0.9
        else:
            return '-'

    elif feature == 'hydrophobic':
        if res1 in PATTERNS['hydrophobic'] and (res2 in PATTERNS['hydrophobic'] or res2 in PATTERNS['amphipatic']):
            return 0.1
        elif res1 in PATTERNS['amphipatic'] and res2 in PATTERNS['hydrophobic']:
            return 0.1
        else:
            return '-'

    elif feature == 'hydrophilic':
        if res1 in PATTERNS['hydrophilic'] and (res2 in PATTERNS['hydrophilic'] or res2 in PATTERNS['amphipatic']):
            return 0.1
        elif res1 in PATTERNS['amphipatic'] and res2 in PATTERNS['hydrophilic']:
            return 0.1
        else:
            return '-'

    elif feature == 'electrostatics':
        if (res1 in PATTERNS['charged'][0] and res2 in PATTERNS['charged'][1]) or (res2 in PATTERNS['charged'][0] and res1 in PATTERNS['charged'][1]):
            return 0.1
        elif (res1 in PATTERNS['charged'][0] or res1 in PATTERNS['charged'][1]) and res2 in PATTERNS['polar']:
            return 0.3
        elif (res2 in PATTERNS['charged'][0] or res2 in PATTERNS['charged'][1]) and res1 in PATTERNS['polar']:
            return 0.3
        elif res1 in PATTERNS['polar'][0] and res2 in PATTERNS['polar']:
            return 0.6
        elif (res1 in PATTERNS['charged'][0] and res2 in PATTERNS['charged'][0]) or (res1 in PATTERNS['charged'][1] and res2 in PATTERNS['charged'][1]):
            return 0.9
        else:
            return '-'

    elif feature == 'π-π stacking':
        if res1 in PATTERNS['aromatic'] and res2 in PATTERNS['aromatic']:
            return 0.1
        elif (res1 in PATTERNS['aromatic'] and res2 in PATTERNS['π-bond']) or (res2 in PATTERNS['aromatic'] and res1 in PATTERNS['π-bond']):
            return 0.5
        elif res1 in PATTERNS['π-bond'] and res2 in PATTERNS['π-bond']:
            return 0.8
        else:
            return '-'

    elif feature == 'π-ion stacking':
        if (res1 in PATTERNS['aromatic'] or res1 in PATTERNS['π-bond']) and res2 in PATTERNS['charged'][0]:
            return 0.1
        elif (res2 in PATTERNS['aromatic'] or res2 in PATTERNS['π-bond']) and res1 in PATTERNS['charged'][0]:
            return 0.1
        if (res1 in PATTERNS['aromatic'] or res1 in PATTERNS['π-bond']) and res2 in PATTERNS['charged'][1]:
            return 0.9
        elif (res2 in PATTERNS['aromatic'] or res2 in PATTERNS['π-bond']) and res1 in PATTERNS['charged'][1]:
            return 0.9
        else:
            return '-'

    else:
        return '-'


PATTERNS = {
    'hydrophobic'     : ['ALA', 'GLY', 'LEU', 'ILE', 'VAL', 'PRO', 'PHE', 'DA', 'DG', 'DT', 'DC', 'A', 'G', 'U', 'C'],
    'amphipatic'      : ['TRP', 'TYR', 'MET', 'LYS'],
    'hydrophilic'     : ['ARG', 'ASN', 'ASP', 'GLN', 'GLU', 'HIS', 'SER', 'THR', 'CYS'],
    'charged'         : [['LYS', 'ARG', 'HIS'], ['GLU', 'ASP', 'DA', 'DG', 'DT', 'DC', 'A', 'G', 'U', 'C']],
    'polar'           : ['CYS', 'MET', 'SER', 'THR', 'TYR', 'GLN', 'ASN', 'DA', 'DG', 'DT', 'DC', 'A', 'G', 'U', 'C'],
    'nonpolar'        : ['ALA', 'GLY', 'ILE', 'LEU', 'VAL', 'PHE', 'PRO', 'TRP'],
    'aromatic'        : ['PHE', 'TYR', 'TRP', 'HIS', 'DA', 'DG', 'DT', 'DC', 'A', 'G', 'U', 'C'],
    'π-bond'          : ['ARG', 'ASN', 'ASP', 'GLN', 'GLU', 'GLY'],
    'sulfur'          : [['MET'], ['CYS']],
    'H-Bond donor'    : ['ARG', 'ASN', 'GLN', 'HIS', 'LYS', 'SER', 'THR', 'TRP', 'TYR'],
    'H-Bond acceptor' : ['ASN', 'ASP', 'GLN', 'GLU', 'HIS', 'SER', 'THR', 'TYR']
}


cs1a = [[0, '#ff0000'], [0.999, '#ff0000'], [1, 'rgba(255,255,255, 0.0)']]
cs1b = [[0, '#1DACD6'], [0.999, '#1DACD6'], [1, 'rgba(255,255,255, 0.0)']]
cs2  = [[0, '#ff0000'], [0.5, '#ff0000'], [0.5, '#1DACD6'], [0.99, '#1DACD6'], [1, 'rgba(255,255,255, 0.0)']]
cs3  = [[0, '#ff0000'], [0.33, '#ff0000'], [0.33, '#cc0066'], [0.66, '#cc0066'], [0.66, '#9900cc'], [0.999, '#9900cc'], [1, 'rgba(255,255,255, 0.0)']]
cs4  = [[0, '#ff0000'], [0.25, '#ff0000'], [0.25, '#cc0066'], [0.5, '#cc0066'], [0.5, '#9900cc'], [0.75, '#9900cc'], [0.75, '#1DACD6'],  [0.999, '#1DACD6'], [1, 'rgba(255,255,255, 0.0)']]
cs5  = [[0, '#ff0000'], [0.2, '#ff0000'], [0.2, '#cc0066'], [0.4, '#cc0066'], [0.4, '#9900cc'], [0.6, '#9900cc'], [0.6, '#3378d3'], [0.8, '#3378d3'], [0.8, '#1DACD6'],  [0.999, '#1DACD6'], [1, 'rgba(255,255,255, 0.0)']]
CS_CONTACT = {
    'none'            : [],
    'hydropathy'      : [cs5, 'Contact filter:<br>hydropathy', 0.22, [0.1, 0.3 , 0.5, 0.7, 0.9], ['ζ-ζ', 'ζ-ɤ', 'ɤ-ɤ', 'Φ-ɤ', 'Φ-Φ']],
    'hydrophobic'     : [cs1b, 'Contact filter:<br>hydrophobic', 0.15, [0.5], ['Φ-Φ + Φ-ɤ']],
    'hydrophilic'     : [cs1a, 'Contact filter:<br>hydrophilic', 0.15, [0.5], ['ζ-ζ + ζ-ɤ']],
    'electrostatics'   : [cs4, 'Contact filter:<br>electrostatics', 0.22, [0.13, 0.38, 0.63, 0.88], ['A: ⊕ ⊖', 'A: ⦿  δ', 'A: δ δ', 'R: ⊕ ⊕ or ⊖ ⊖']],
    'π-π stacking'    : [cs3, 'Contact filter:<br>π-π stacking', 0.22, [0.17, 0.5, 0.79], ['⌬-⌬', '⌬-π', 'π-π']],
    'π-ion stacking'  : [cs2, 'Contact filter:<br>π-ion stacking', 0.17, [0.25, 0.75], ['⊕-π', '⊖-π']],
    'hydrogen bonds'  : [cs1a, 'Contact filter:<br>hydrogen bond', 0.15, [0.5], ['HB']],
    'distance'        : [ '', 'distance', 0.4, [], []],
    'contact'         : [ '', 'contact', 0.1, [0.5], ['contact']]
}


AA_CODES = {
    'A': 'ALA', 'C': 'CYS', 'D': 'ASP', 'E': 'GLU', 'F': 'PHE',
    'G': 'GLY', 'H': 'HIS', 'I': 'ILE', 'K': 'LYS', 'L': 'LEU',
    'M': 'MET', 'N': 'ASN', 'P': 'PRO', 'Q': 'GLN', 'R': 'ARG',
    'S': 'SER', 'T': 'THR', 'V': 'VAL', 'W': 'TRP', 'Y': 'TYR'
}


A_CODE = {
    'ALA': 'A', 'CYS': 'C', 'ASP': 'D', 'GLU': 'E', 'PHE': 'F',
    'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LYS': 'K', 'LEU': 'L',
    'MET': 'M', 'ASN': 'N', 'PRO': 'P', 'GLN': 'Q', 'ARG': 'R',
    'SER': 'S', 'THR': 'T', 'VAL': 'V', 'TRP': 'W', 'TYR': 'Y'
}

N_CODE = {
    'DA': 'A', 'DC': 'C', 'DG': 'G', 'DT': 'T',
    'A': 'A', 'C': 'C', 'G': 'G', 'U': 'U'
}


# id - mass - frequency - charge - aromatic - KD_hydropathy - color - sa (doi: https://doi.org/10.1371/journal.pone.0080635) [teoret, exp, Miller_1987, Rose_1985]
AA_ATTRIBUTES = {
    'ALA': [ 0,  89.094, 8.76,  0.0, 0.0,  1.8, 0.75, [129, 121, 113, 118.1]],
    'CYS': [ 1, 121.154, 1.38,  0.0, 0.0,  2.5, 0.90, [167, 148, 140, 146.1]],
    'ASP': [ 2, 133.104, 5.49, -1.0, 0.0, -3.5, 0.25, [193, 187, 151, 158.7]],
    'GLU': [ 3, 147.131, 6.32, -1.0, 0.0, -3.5, 0.30, [223, 214, 183, 186.2]],
    'PHE': [ 4, 165.192, 3.87,  0.0, 1.0,  2.8, 0.05, [240, 228, 218, 222.8]],
    'GLY': [ 5,  75.067, 7.03,  0.0, 0.0, -0.4, 0.80, [104,  97,  85,  88.1]],
    'HIS': [ 6, 155.156, 2.26,  0.5, 1.0, -3.2, 0.45, [224, 216, 194, 202.5]],
    'ILE': [ 7, 131.175, 5.49,  0.0, 0.0,  4.5, 0.65, [197, 195, 182, 181.0]],
    'LYS': [ 8, 146.189, 5.19,  1.0, 0.0, -3.9, 0.50, [236, 230, 211, 225.8]],
    'LEU': [ 9, 131.175, 9.68,  0.0, 0.0,  3.8, 0.60, [201, 191, 180, 193.1]],
    'MET': [10, 149.208, 2.32,  0.0, 0.0,  1.9, 0.85, [224, 203, 204, 203.4]],
    'ASN': [11, 132.119, 3.93,  0.0, 0.0, -3.5, 0.15, [195, 187, 158, 165.5]],
    'PRO': [12, 115.132, 5.02,  0.0, 0.0, -1.6, 0.95, [159, 154, 143, 146.8]],
    'GLN': [13, 146.146, 3.90,  0.0, 0.0, -3.5, 0.20, [225, 214, 189, 193.2]],
    'ARG': [14, 174.203, 5.78,  1.0, 0.0, -4.5, 0.55, [274, 265, 241, 256.0]],
    'SER': [15, 105.093, 7.14,  0.0, 0.0, -0.8, 0.35, [155, 143, 122, 129.8]],
    'THR': [16, 119.119, 5.53,  0.0, 0.0, -0.7, 0.40, [172, 163, 146, 152.5]],
    'VAL': [17, 117.148, 6.73,  0.0, 0.0,  4.2, 0.70, [174, 165, 160, 164.5]],
    'TRP': [18, 204.228, 1.25,  0.0, 1.0, -0.9, 0.00, [285, 264, 259, 266.3]],
    'TYR': [19, 181.191, 2.91,  0.0, 1.0, -1.3, 0.10, [263, 255, 229, 236.8]],
     'DA': [20, 331.200, 2.52, -1.0, 1.0, -2.8, 0.10, [400, 400, 400, 400]],
     'DG': [20, 347.200, 2.48, -1.0, 1.0, -6.7, 0.10, [400, 400, 400, 400]],
     'DT': [20, 322.200, 2.51, -1.0, 1.0, -2.2, 0.10, [350, 350, 350, 350]],
     'DC': [20, 307.200, 2.52, -1.0, 1.0, -6.0, 0.10, [350, 350, 350, 350]],
      'A': [20, 347.200, 2.50, -1.0, 1.0, -2.8, 0.10, [400, 400, 400, 400]],
      'G': [20, 363.200, 2.50, -1.0, 1.0, -6.7, 0.10, [400, 400, 400, 400]],
      'U': [20, 324.200, 2.50, -1.0, 1.0, -3.7, 0.10, [350, 350, 350, 350]],
      'C': [20, 323.200, 2.50, -1.0, 1.0, -6.0, 0.10, [350, 350, 350, 350]],
}


INTERACTION = {
     '0:0': ['F'],  '0:1': ['F'],  '0:2': ['I'],  '0:3': ['I'],  '0:4': ['F'],
     '0:5': ['F'],  '0:6': ['I'],  '0:7': ['F'],  '0:8': ['F'],  '0:9': ['F'],
    '0:10': ['F'], '0:11': ['I'], '0:12': ['F'], '0:13': ['I'], '0:14': ['I'],
    '0:15': ['I'], '0:16': ['I'], '0:17': ['F'], '0:18': ['F'], '0:19': ['F'],
     '1:1': ['S', 'D'], '1:2': ['E', 'H'],  '1:3': ['E', 'H'],  '1:4': ['F'],
     '1:5': ['F'], '1:6': ['E', 'H'], '1:7': ['F'], '1:8': ['E', 'H'],
     '1:9': ['F'], '1:10': ['D'], '1:11': ['D', 'H'], '1:12': ['F'],
    '1:13': ['D', 'H'], '1:14': ['E', 'H'], '1:15': ['D', 'H'], '1:16': ['D', 'H'],
    '1:17': ['F'], '1:18': ['F'], '1:19': ['D', 'H'], '2:2': ['R'], '2:3': ['R'],
     '2:4': ['A'], '2:5': ['I'], '2:6': ['B', 'H', 'A'], '2:7': ['I'], '2:8': ['B', 'H'],
     '2:9': ['I'], '2:10': ['E'], '2:11': ['E', 'H'], '2:12': ['I'], '2:13': ['E', 'H'],
    '2:14': ['B', 'H'], '2:15': ['E', 'H'], '2:16': ['E', 'H'], '2:17': ['I'],
    '2:18': ['A', 'P', 'H'], '2:19': ['A', 'P', 'E', 'H'], '3:3': ['R'],  '3:4': ['A'],
     '3:5': ['I'], '3:6': ['B', 'H', 'A'], '3:7': ['I'], '3:8': ['B', 'H'], '3:9': ['I'],
    '3:10': ['E'], '3:11': ['E', 'H'], '3:12': ['I'], '3:13': ['E', 'H'], '3:14': ['B', 'H'],
    '3:15': ['E', 'H'], '3:16': ['E', 'H'], '3:17': ['I'], '3:18': ['A', 'P', 'H'],
    '3:19': ['A', 'P', 'E', 'H'], '4:4': ['P', 'F'],  '4:5': ['F'],  '4:6': ['C', 'P'],
     '4:7': ['F'], '4:8': ['C'], '4:9': ['F'], '4:10': ['F', 'O'], '4:11': ['P'],
    '4:12': ['F'], '4:13': ['P'], '4:14': ['C'], '4:15': ['O'], '4:16': ['O'], '4:17': ['F'],
    '4:18': ['P', 'F'], '4:19': ['P', 'F', 'O'], '5:5': ['F'],  '5:6': ['I'],  '5:7': ['F'],
     '5:8': ['F'], '5:9': ['F'], '5:10': ['F'], '5:11': ['I'], '5:12': ['F'], '5:13': ['I'],
    '5:14': ['I'], '5:15': ['I'], '5:16': ['I'], '5:17': ['F'], '5:18': ['F'], '5:19': ['F'],
     '6:6': ['R', 'H', 'C', 'P'],  '6:7': ['I'], '6:8': ['R', 'H'],  '6:9': ['I'],
    '6:10': ['E', 'H'], '6:11': ['E', 'H', 'P', 'O'], '6:12': ['I'], '6:13': ['E','H','P', 'O'],
    '6:14': ['R', 'H', 'C'], '6:15': ['E', 'H', 'O'], '6:16': ['E', 'H', 'O'], '6:17': ['I'],
    '6:18': ['C', 'P', 'H'], '6:19': ['C', 'P', 'H', 'O'], '7:7': ['F'],  '7:8': ['F'],
     '7:9': ['F'], '7:10': ['F'], '7:11': ['I'], '7:12': ['F'], '7:13': ['I'], '7:14': ['I'],
    '7:15': ['I'], '7:16': ['I'], '7:17': ['F'], '7:18': ['F'], '7:19': ['F'], '8:8': ['R', 'F'],
     '8:9': ['F'], '8:10': ['E', 'H', 'F'], '8:11': ['E', 'H'], '8:12': ['I'], '8:13': ['E', 'H'],
    '8:14': ['R'], '8:15': ['E', 'H'], '8:16': ['E', 'H'], '8:17': ['F'], '8:18': ['C', 'F'],
    '8:19': ['C', 'H'], '9:9': ['F'], '9:10': ['F'], '9:11': ['I'], '9:12': ['F'], '9:13': ['I'],
    '9:14': ['I'], '9:15': ['I'], '9:16': ['I'], '9:17': ['F'], '9:18': ['F'], '9:19': ['F'],
   '10:10': ['F', 'D'], '10:11': ['D', 'H'], '10:12': ['F'], '10:13': ['D', 'H'],
   '10:14': ['E', 'H'], '10:15': ['D', 'H'], '10:16': ['D', 'H'], '10:17': ['F'],
   '10:18': ['F', 'O', 'H'], '10:19': ['D', 'H', 'O'], '11:11': ['D', 'H'], '11:12': ['I'],
   '11:13': ['D', 'H'], '11:14': ['E', 'H'], '11:15': ['D', 'H'], '11:16': ['D', 'H'],
   '11:17': ['I'], '11:18': ['H', 'P', 'O'], '11:19': ['D', 'H', 'P', 'O'], '12:12': ['F'],
   '12:13': ['I'], '12:14': ['I'], '12:15': ['I'], '12:16': ['I'], '12:17': ['F'], '12:18': ['F'],
   '12:19': ['F'], '13:13': ['D', 'H'], '13:14': ['E', 'H'], '13:15': ['D', 'H'],
   '13:16': ['D', 'H'], '13:17': ['I'], '13:18': ['H', 'P', 'O'], '13:19': ['D', 'H', 'P', 'O'],
   '14:14': ['R', 'P'], '14:15': ['E', 'H'], '14:16': ['E', 'H'], '14:17': ['I'], '14:18': ['C'],
   '14:19': ['C', 'P', 'H'], '15:15': ['D', 'H'], '15:16': ['D', 'H'], '15:17': ['I'],
   '15:18': ['H', 'O'], '15:19': ['D', 'H', 'O'], '16:16': ['D', 'H'], '16:17': ['I'],
   '16:18': ['H', 'O'], '16:19': ['D', 'H', 'O'], '17:17': ['F'], '17:18': ['F'], '17:19': ['F'],
   '18:18': ['P', 'F'], '18:19': ['H', 'P', 'O'], '19:19': ['H', 'P', 'O', 'F'],
   '20:20': ['Hn', 'Pn', 'D'], '0:20': ['Fb', 'Hb', 'I'], '1:20': ['H', 'Ep', 'Ds', 'Db'],
   '2:20': ['H', 'Rp', 'Es', 'Ab', 'Pb'], '3:20': ['H', 'Rp', 'Es', 'Ab', 'Pb'],
   '4:20': ['Ap', 'Pb', 'Fb', 'Hb'], '5:20': ['Fb', 'Hb', 'I'], '6:20': ['H', 'Bp', 'Es', 'Cb', 'Pb'],
   '7:20': ['Fb', 'Hb', 'I'], '8:20': ['H', 'Bp', 'Es', 'Cb'], '9:20': ['Fb', 'Hb', 'I'],
   '10:20': ['H', 'Ep', 'Ds', 'Db'], '11:20': ['H', 'Ep', 'Ds', 'Db',  'Pb'], '12:20': ['Fb', 'Hb', 'I'],
   '13:20': ['H', 'Ep', 'Ds', 'Db', 'Pb'], '14:20': ['H', 'Bp', 'Es', 'Cb'], '15:20': ['H', 'Ep', 'Ds', 'Db'],
   '16:20': ['H', 'Ep', 'Ds', 'Db'], '17:20': ['Fb', 'Hb', 'I'], '18:20': ['H', 'Ap', 'Pb'],
   '19:20': ['H', 'Ap', 'Ds', 'Pb', 'Fb']
}


DESCRIPTORS = {
    'S': '- covalent sulfide bridge,<br>',
    'B': '- salt bridge,<br>',
    'R': '- ionic repulsion <br>CAUTION: possible repulsion<br>',
    'E': '- electrostatic: ion-dipole,<br>',
    'H': '- hydrogen bond,<br>',
    'D': '- electrostatic: dipole-dipole,<br>',
    'F': '- hydrophobic,<br>',
    'C': '- cation-π stacking,<br>',
    'A': '- anion-π stacking,<br>',
    'M': '- metal-π stacking,<br>',
    'P': '- π-π stacking,<br>',
    'O': '- dipole-π stacking<br>',
    'W': '- CH-π stacking,<br>',
    'I': '- induction + dispersion<br>',
   'Hb': '- hydrogen bond with AA backbone,<br>',
   'Fb': '- hydrophobic with NA base,<br>',
   'Bp': '- salt bridge with NA phosphate,<br>',
   'Rp': '- ionic repulsion with NA phosphate,<br>',
   'Ep': '- electrostatic: ion-dipole with NA phosphate,<br>',
   'Es': '- electrostatic: ion-dipole with NA sugar,<br>',
   'Ds': '- electrostatic: dipole-dipole with NA sugar,<br>',
   'Db': '- electrostatic: dipole-dipole with NA base,<br>',
   'Cb': '- cation-π stacking with NA base,<br>',
   'Pb': '- π-π stacking with NA base,<br>',
   'Ab': '- anion-π stacking with NA base,<br>',
   'Ap': '- anion-π stacking with NA phosphate,<br>',
   'Hn': '- hydrogen bond between bases,<br>',
   'Pn': '- π-π stacking between aromatic bases,<br>',
}


SS_CODES = {
    '3-letter': {'C': 0.2, 'H': 0.5, 'E': 0.8},
    '8-letter': {'H': 0.05, 'G': 0.15, 'I': 0.30, 'E': 0.43, 'B': 0.55, 'T': 0.65, 'S': 0.78, 'C': 0.90}, #(H,G,I,E,B,T,S,C)
}
