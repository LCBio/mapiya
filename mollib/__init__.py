__version__ = '1.0'
from django.conf import settings
if hasattr(settings, 'PDB_CACHE'):
    from .atom import PdbFile
    PdbFile.PDB_CACHE = settings.PDB_CACHE
