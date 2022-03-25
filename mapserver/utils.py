import io
import re

def validate(file_to_validate):

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

    counter = 0

    text_file_to_validate=io.TextIOWrapper(file_to_validate.file, encoding='utf-8')

    for line in text_file_to_validate:
        if re.match(ATOM_PATT, line): counter += 1

    text_file_to_validate.detach()

    if counter > 10:
        return None
    else:
        return 'Wrong file type'
