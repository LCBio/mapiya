import re
import io
from django.core.files import File

def validate(request, file_id):

    ATOM_PATT = re.compile('''
        [ATOM]
    ''', re.X)

    '''counter = 0
    pdb = File(file=request.FILES[file_id].file, name=request.FILES[file_id].name)
    f=io.TextIOWrapper(pdb, encoding='utf-8')
    print(f)'''


    return True
