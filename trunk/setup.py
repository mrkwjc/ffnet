#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
metadata = {}
if (len(sys.argv) >= 2
        and ('--help' in sys.argv[1:] or sys.argv[1]
             in ('--help-commands', 'egg_info', '--version', 'clean'))):

    # For these actions, NumPy is not required.
    #
    # They are required to succeed without Numpy for example when
    # pip is used to install Scikit when Numpy is not yet present in
    # the system.
    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup
    try:
        import numpy
    except ImportError:
        metadata['setup_requires'] = ['numpy>=1.4']
else:
    from numpy.distutils.core import setup
    from numpy.distutils.core import Extension
    try:
       from distutils.command.build_py import build_py_2to3 \
            as build_py
    except ImportError:
       from distutils.command.build_py import build_py

    ext1 = Extension(name = 'ffnet.fortran._ffnet',
                     sources = ['ffnet/fortran/ffnet.f'])

    ext2 = Extension(name = 'ffnet.fortran._pikaia',
                     sources = ['ffnet/fortran/pikaia.f'])

    metadata['cmdclass'] = {'build_py': build_py}
    metadata['ext_modules'] = [ext1, ext2]

if __name__ == "__main__":
    setup(name              = 'ffnet',
          version           = '0.8.0',
          description       = 'Feed-forward neural network solution for python',
          long_description  = '"ffnet" is a fast and easy-to-use feed-forward neural network training solution for python. Many nice features are implemented: arbitrary network connectivity, automatic data normalization, very efficient training tools, support for multicore systems, network export to fortran code...',
          author            = 'Marek Wojciechowski',
          author_email      = 'mwojc@p.lodz.pl',
          url               = 'ffnet.sourceforge.net',
          license           = 'GPL',
          platforms         = 'Posix, Windows',
          package_dir       = {'ffnet': 'ffnet', 
                               'ffnet.fortran': 'ffnet/fortran',
                               'ffnet.examples': 'examples'},
          packages          = ['ffnet', 'ffnet.fortran', 'ffnet.examples'],
          package_data      = {'ffnet.fortran': ['ffnet.f', 'pikaia.f'],
                               'ffnet.examples': ['data/*']
                               },
          install_requires  = ['numpy>=1.4', 'scipy>=0.8', 'networkx>=1.3'],
          **metadata
          )
