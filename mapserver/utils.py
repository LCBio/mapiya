import re
import io
from django.core.files import File

def validate(file):

    ATOM_PATT = re.compile('''
        [ATOM]
    ''', re.X)

    counter = 0

    f=io.TextIOWrapper(file, encoding='utf-8')
    print(f.read())


    return True
