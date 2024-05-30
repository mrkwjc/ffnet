#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.cmd import Command
from setuptools.command.build_py import build_py
from setuptools.dist import Distribution
import distutils.log
import subprocess
import os
import sys

major = sys.version_info.major
minor = sys.version_info.minor
meson = ['meson', 'meson-python'] if (major == 3 and minor >= 12) else []


class F2PyCommand(Command):
    """A custom command to run F2Py on Fortran source files."""

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run command."""
        build_lib = self.distribution._ffnet_build_lib
        os.chdir(os.path.join(build_lib, 'ffnet/fortran'))
        sources = ['ffnet.f', 'pikaia.f']
        modules = ['_ffnet', '_pikaia']
        for s, m in zip(sources, modules):
            cmd = ['f2py', '-m', m, '-c', s]
            self.announce(
                f'Compiling Fortran extension: {str(cmd)}',
                level=distutils.log.INFO)
            subprocess.check_call(cmd)
        os.chdir('../../../..')


class BuildPyCommand(build_py):
    """A custom build command"""

    def run(self):
        """Run command."""
        build_py.run(self)
        self.distribution._ffnet_build_lib = self.build_lib
        self.run_command('f2py')


class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""

    def has_ext_modules(self):
        return True


if __name__ == "__main__":
    setup(
        cmdclass          = {'f2py': F2PyCommand,
                             'build_py': BuildPyCommand},
        distclass         = BinaryDistribution,
        name              = 'ffnet',
        version           = '0.8.6',
        description       = 'Feed-forward neural network solution for python',
        long_description  = open('README.md', 'r').read(),
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
        install_requires  = ['numpy'] + meson,
        classifiers       = ['Development Status :: 4 - Beta',
                             'Environment :: Console',
                             'Intended Audience :: Education',
                             'Intended Audience :: End Users/Desktop',
                             'Intended Audience :: Science/Research',
                             'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                             'Operating System :: OS Independent',
                             'Programming Language :: Fortran',
                             'Programming Language :: Python',
                             'Topic :: Scientific/Engineering :: Artificial Intelligence'],
          )
