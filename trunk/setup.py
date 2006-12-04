#!/usr/bin/env python

from numpy.distutils.core import Extension

ext1 = Extension(name = '_ffnet',
                 sources = ['fortran/ffnet.f'])

ext2 = Extension(name = '_pikaia',
                 sources = ['fortran/pikaia.f'])

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(name              = 'ffnet',
          description       = "Feed-forward neural network solution for python",
          author            = "Marek Wojciechowski",
          author_email      = "mwojc@p.lodz.pl",
          ext_modules       = [ext1, ext2],
          py_modules        = ["ffnet", "pikaia"]
          )

