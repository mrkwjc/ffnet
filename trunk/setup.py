#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy.distutils.core import Extension
try:
   from distutils.command.build_py import build_py_2to3 \
        as build_py
except ImportError:
   from distutils.command.build_py import build_py

ext1 = Extension(name = 'ffnet.fortran._ffnet',
                 sources = ['src/fortran/ffnet.f'])

ext2 = Extension(name = 'ffnet.fortran._pikaia',
                 sources = ['src/fortran/pikaia.f'])

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(name              = 'ffnet',
          version           = '0.8.0',
          description       = 'Feed-forward neural network solution for python',
          long_description  = '"ffnet" is a fast and easy-to-use feed-forward neural network training solution for python. Many nice features are implemented: arbitrary network connectivity, automatic data normalization, very efficient training tools, support for multicore systems, network export to fortran code...',
          author            = 'Marek Wojciechowski',
          author_email      = 'mwojc@p.lodz.pl',
          url               = 'ffnet.sourceforge.net',
          license           = 'GPL',
          platforms         = 'Posix, Windows',
          package_dir       = {'ffnet': 'src', 
                               'ffnet.fortran': 'src/fortran',
                               'ffnet.examples': 'examples'},
          packages          = ['ffnet', 'ffnet.fortran', 'ffnet.examples'],
          ext_modules       = [ext1, ext2],
          package_data      = {'ffnet.fortran': ['ffnet.f', 'pikaia.f'],
                               'ffnet.examples': ['data/*']
                               },
          cmdclass = {'build_py': build_py}
          )
