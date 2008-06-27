from numpy import f2py
import os

files = os.listdir('.')
for file in files:
    name, ext = os.path.splitext(file)
    if ext == '.f':
        print "Compiling file %s." %file
        f2py.compile(open(file, 'r').read(), '_' + name)
