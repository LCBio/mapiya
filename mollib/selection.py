"""
Module for selecting subset of atoms from Atoms() object.
usage: Atoms().select(selection_string) or Atoms().drop(selection_string)
"""

import re
from cached_property import cached_property
from collections import OrderedDict

# one-word keywords
BOOL_KEYWORDS = ['HETERO', 'HYDRO']

# keywords accepting arguments
CHAR_KEYWORDS = ['CHAIN', 'ALTLOC', 'ICODE']
STR_KEYWORDS = ['RESNAME', 'NAME', 'RESID']
INT_KEYWORDS = ['MODEL', 'RESNUM', 'SERIAL']
FLOAT_KEYWORDS = ['BFAC', 'OCC']
ARGS_KEYWORDS = CHAR_KEYWORDS + STR_KEYWORDS + INT_KEYWORDS + FLOAT_KEYWORDS

# shortcut aliases
ALIASES = OrderedDict([
    ('BACKBONE', 'PROTEIN and name N,CA,C,O'),
    ('SIDECHAIN', 'PROTEIN and not name N,CA,C,O'),
    ('HEAVY', 'not HYDRO'),
    ('HETATM', 'HETERO'),
    ('WATER', 'resname HOH'),
    ('PROTEIN', 'resname ALA,CYS,ASP,GLU,PHE,GLY,HIS,ILE,LYS,LEU,MET,ASN,PRO,GLN,ARG,SER,THR,VAL,TRP,TYR'),
])

# logical operators
OPERATORS = ['NOT', 'AND', 'OR']

# parenthesis
PARENTHESIS = ['(', ')']

# joints between keywords
JOINTS = OPERATORS + PARENTHESIS

# all keywords combined
KEYWORDS = BOOL_KEYWORDS + ARGS_KEYWORDS

# all tokens combined
TOKENS = KEYWORDS + JOINTS

# help to be imported
SYNTAX = '''
SELECTION syntax:

* Selection sentence is a combination of keywords and operators.
* Keywords may be followed by argument(s).
* Keywords and operators are case-insensitive, while arguments aren't.
* If used in the command line, selection sentence must be enclosed in "".

I. Keywords

1. No argument keywords:
HETERO      selects non-protein atoms
HYDRO       selects hydrogen atoms

2. Keywords with character arguments:
CHAIN       selects by chain id
ALTLOC      selects by alternative locations
ICODE       selects by insertion codes

examples:   altloc A
            chain A, B, C

3. Keywords with string arguments:
NAME        selects by atom name
RESNAME     selects by residue name
RESID       selects by residue id (number + insertion code)

examples:   name CA
            resname VAL, ILE
            resid 123, 123A
            
4. Keywords with integer arguments:
MODEL       selects by model number
RESNUM      selects by residue number
SERIAL      selects by serial number

examples:   model 1
            resnum 25-33
            
5. Keywords with float arguments:
BFAC        selects by beta factor
OCC         selects by occupancy

examples:   bfac 0.1-0.5, 0.75-0.9
            occ 1.0

II. Operators

,           separates multiple arguments for one keyword
            i.e. "name N, CA, C, O" selects all atom with names N, CA, C and O
            
+           alias for ,
            i.e. "name N+CA+C+O" selects all atom with names N, CA, C and O
            
-           range operator
            i.e. "resnum 25-33" selects all atoms in residues with numbers from 25 to 33
            works also with character args
            i.e. "chain A-D" is equivalent to chain A+B+C+D

NOT         negation logical operator, negates following keyword
            i.e. "not chain A" selects all chains except for chain A

AND         logical conjunction
            i.e. "chain A and name CA" selects all CA atoms in chain A
            
OR          logical alternation
            i.e. "chain A or chain B" selects all atoms in chain A or chain B
            
()          parenthesis can be used to group expressions to be evaluated together

III. Aliases

Aliases are shortcuts for frequent selections.                
{}
'''.format('\n'.join(['{:10} == {}'.format(key, val) for key, val in ALIASES.items()]))


# helper function to merge overlapping intervals
def merge_intervals(intervals):

    if not intervals:
        return []

    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged_intervals = [sorted_intervals[0]]

    for interval in sorted_intervals[1:]:
        if interval[0] <= merged_intervals[-1][1]:
            merged_intervals[-1] = (merged_intervals[-1][0], max(merged_intervals[-1][1], interval[1]))
        else:
            merged_intervals.append(interval)

    return merged_intervals


# exception raised when invalid string is used to initialize Selection object
class InvalidSelectionSyntax(Exception):

    def __init__(self, selection_string):
        self.selection_string = selection_string

    def __str__(self):
        return 'Invalid selection string "{}"'.format(self.selection_string)


class Token:

    def __init__(self, keyword, arg=None):
        self.keyword = keyword.lower()
        self.args = arg.split(',') if arg else []

    def match(self, atom):
        return getattr(atom, self.keyword)

    def __str__(self):
        return self.keyword + ': ' + ','.join(self.args) if self.args else self.keyword


class ValueToken(Token):

    def __init__(self, keyword, arg, arg_type):
        super().__init__(keyword, arg)
        self.arg_type = arg_type

    @cached_property
    def values(self):
        return [self.arg_type(val) for val in self.args if '-' not in val]

    def match(self, atom):
        attr = getattr(atom, self.keyword)
        return attr in self.values


class RangeToken(ValueToken):

    @cached_property
    def ranges(self):
        return [(self.arg_type(r[0]), self.arg_type(r[1])) for r in merge_intervals(
            [val.split('-') for val in self.args if '-' in val]
        )]

    def match(self, atom):
        attr = getattr(atom, self.keyword)
        return attr in self.values or any(map(lambda r: r[0] <= attr <= r[1], self.ranges))


class JointToken(Token):

    def match(self, atom):
        return self.keyword


class Selection:
    """
    Class used to select subset of atoms from the Atoms() object.
    """

    def __init__(self, selection):

        # substitute aliases
        for key, val in ALIASES.items():
            selection = re.sub(key, val, selection, flags=re.I)

        # substitute plus-signs with commas
        selection = selection.replace('+', ',')

        # remove whitespaces from around commas and minus-signs
        selection = re.sub(r'\s*,\s*', ',', selection)
        selection = re.sub(r'\s*-\s*', '-', selection)

        # make sure parenthesis have whitespaces around
        selection = selection.replace('(', ' ( ').replace(')', ' ) ')

        # generate tokens
        self.tokens = []
        word = iter(selection.split())
        while True:
            try:
                keyword = next(word)
                keyword = keyword.upper()

                if keyword in JOINTS:
                    self.tokens.append(JointToken(keyword))

                elif keyword in BOOL_KEYWORDS:
                    self.tokens.append(Token(keyword))

                elif keyword in CHAR_KEYWORDS:
                    arg = next(word)
                    self.tokens.append(RangeToken(keyword, arg, str))

                elif keyword in STR_KEYWORDS:
                    arg = next(word)
                    self.tokens.append(ValueToken(keyword, arg, str))

                elif keyword in INT_KEYWORDS:
                    arg = next(word)
                    self.tokens.append(RangeToken(keyword, arg, int))

                elif keyword in FLOAT_KEYWORDS:
                    arg = next(word)
                    self.tokens.append(RangeToken(keyword, arg, float))

                else:
                    raise InvalidSelectionSyntax(selection)

            except StopIteration:
                break

    def __str__(self):
        return ' '.join([str(token) for token in self.tokens])

    def __repr__(self):
        return str(self)

    def match(self, atom):
        pattern = [str(token.match(atom)) for token in self.tokens]
        return eval(" ".join(pattern)) if pattern else False
