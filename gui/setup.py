#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

metadata = {'setup_requires':   [],
            'install_requires': ['ffnet>=0.8.1',
                                 'traitsui>=4.4',
                                 'matplotlib>=1.4']}

try:
    import wx
    if wx.VERSION[0] == 2 and wx.VERSION[1] == 8:
        pass
    else:
        raise ImportError
except ImportError:
    try:
        import PySide
    except ImportError:
        import PyQt4
    else:
        metadata['install_requires'] += ['pyside>=1.2']  # Install also pyside if no backend is found


if __name__ == "__main__":
    setup(name              = 'ffnetui',
          version           = '0.8.1',
          description       = 'GUI for ffnet - feed-forward neural network for python',
          long_description  = 'GUI for ffnet - feed-forward neural network for python',
          author            = 'Marek Wojciechowski',
          author_email      = 'mwojc@p.lodz.pl',
          url               = 'ffnet.sourceforge.net',
          license           = 'GPL-3',
          platforms         = 'Posix, Windows',
          package_dir       = {'ffnetui': '.', 
                               'ffnetui.plots': 'plots'},
          packages          = ['ffnetui', 'ffnetui.plots'],
          package_data      = {'ffnetui': ['data/*', 'images/*.*'],
                               'ffnetui.plots': ['images/*.*']},
          entry_points      = {'console_scripts': ['ffnetui = ffnetui:main']},
          **metadata
          )
