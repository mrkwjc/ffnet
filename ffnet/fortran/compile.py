from __future__ import print_function
from numpy import f2py
import os

files = os.listdir('.')
for file in files:
    name, ext = os.path.splitext(file)
    if ext == '.f':
        print('Compiling file {}.'.format(file))
        f2py.compile(open(file, 'rb').read(), '_' + name)
