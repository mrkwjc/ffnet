#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

metadata = {}

if __name__ == "__main__":
    setup(name              = 'ffnetui',
          version           = '0.8.1',
          description       = 'User interface for ffnet - feed-forward neural network for python',
          long_description  = 'User interface for ffnet - feed-forward neural network for python',
          author            = 'Marek Wojciechowski',
          author_email      = 'mwojc@p.lodz.pl',
          url               = 'ffnet.sourceforge.net',
          license           = 'GPLv2',
          platforms         = 'Posix, Windows',
          package_dir       = {'ffnetui': '.', 
                               'ffnetui.plots': 'plots'},
          packages          = ['ffnetui', 'ffnetui.plots'],
          package_data      = {'ffnetui': ['data/*', 'images/*.*'],
                               'ffnetui.plots': ['images/*.*']},
          entry_points      = {'console_scripts': ['ffnetui = ffnetui.ffnetui:main']},
          install_requires  = ['ffnet>=0.8.1', 'traitsui>=4.4', 'matplotlib>=1.4'],
          **metadata
          )
