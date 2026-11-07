"""Keep user-selected final files separate from program resources and caches."""
import os
from pathlib import Path
from .paths import ROOT,HOME

PROTECTED = {'.git','.setup','.bootstrap','.runtime','.cache','assets','cache',
             'character_work','character_scenes','character_library','config','models','mocap','tools',
             'installer','prebuilt','third_party','native_compat'}


def destination(filename, extension, *, root=None, protected_roots=(), protected_files=()):
    path = Path(filename)
    if not path.is_absolute():
        raise ValueError('Export destination must be an absolute user-selected path.')
    if path.is_dir():
        raise ValueError('Export destination must be a file, not a directory.')
    if not path.suffix:
        path = path.with_suffix('.'+extension)
    path = path.resolve()
    if path.suffix.lower() != '.'+extension or path.is_dir():
        raise ValueError('Export destination must be a .'+extension+' file.')
    roots = {ROOT.resolve(),HOME.resolve(),Path(root).resolve() if root is not None else ROOT.resolve()}
    for installation in roots:
        for name in PROTECTED:
            if path.is_relative_to((installation/name).resolve()):
                raise ValueError('Export destination is inside protected program resources or caches.')
        if path.is_relative_to(installation) and path.relative_to(installation).parts[0].startswith('runtime'):
            raise ValueError('Export destination is inside a protected runtime directory.')
        for runtime in installation.glob('runtime*'):
            if runtime.is_dir() and path.is_relative_to(runtime.resolve()):
                raise ValueError('Export destination is inside a protected runtime directory.')
    for folder in protected_roots:
        if path.is_relative_to(Path(folder).resolve()):
            raise ValueError('Export destination would overwrite character input data.')
    for original in protected_files:
        original = Path(original).resolve()
        if path == original or (path.exists() and original.exists() and os.path.samefile(path,original)):
            raise ValueError('Export destination would overwrite an original character FBX.')
    if not path.parent.is_dir():
        raise ValueError('Export destination folder does not exist.')
    return path
