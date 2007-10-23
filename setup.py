#!/usr/bin/env python

from numpy.distutils.core import Extension
from _version import version

ext1 = Extension(name = 'ffnet.fortran._ffnet',
                 sources = ['fortran/ffnet.f'])

ext2 = Extension(name = 'ffnet.fortran._pikaia',
                 sources = ['fortran/pikaia.f'])

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(name              = 'ffnet',
          version           = version,
          description       = "Feed-forward neural network solution for python",
          author            = "Marek Wojciechowski",
          author_email      = "mwojc@p.lodz.pl",
          url               = 'ffnet.sourceforge.net',
          license           = 'GPL',
          platforms         = 'Posix, Windows',
          packages          = [ 'ffnet', 'ffnet.fortran', 'ffnet.tools' ],
          package_dir       = { 'ffnet': '.' },
          data_files        = [ ('ffnet/fortran', [ 'fortran/ffnet.f' ]) ],
          ext_modules       = [ ext1, ext2 ]
          )
          
#         ('ffnet/examples/data', [ 'examples/data/ocr.dat' ])],