#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
try:
    import setuptools
except ImportError:
    pass
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
          version           = '0.8.4',
          description       = 'Feed-forward neural network solution for python',
          long_description  = open('README.rst', 'r').read(),
          keywords          = ['neural networks'],
          author            = 'Marek Wojciechowski',
          author_email      = 'mwojc@p.lodz.pl',
          url               = 'http://ffnet.sourceforge.net',
          license           = 'LGPL-3',
          platforms         = 'Posix, Windows',
          package_dir       = {'ffnet': 'ffnet', 
                               'ffnet.fortran': 'ffnet/fortran',
                               'ffnet.examples': 'examples'},
          packages          = ['ffnet', 'ffnet.fortran', 'ffnet.examples'],
          package_data      = {'ffnet.fortran': ['ffnet.f', 'pikaia.f'],
                               'ffnet.examples': ['data/*']
                               },
          requires          = ['numpy', 'scipy', 'networkx'],
          # install_requires  = ['numpy>=1.4', 'scipy>=0.8', 'networkx>=1.3'],
          classifiers       = ['Development Status :: 4 - Beta',
                               'Environment :: Console',
                               'Intended Audience :: Education',
                               'Intended Audience :: End Users/Desktop',
                               'Intended Audience :: Science/Research',
                               'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                               'Operating System :: OS Independent',
                               'Programming Language :: Fortran',
                               'Programming Language :: Python :: 2.6',
                               'Programming Language :: Python :: 2.7',
                               'Programming Language :: Python :: 3.4',
                               'Programming Language :: Python :: 3.5',
                               'Topic :: Scientific/Engineering :: Artificial Intelligence'],
          **metadata
          )
