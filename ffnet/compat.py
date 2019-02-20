#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 12:18:04 2018

@author: mwojc
"""
from __future__ import absolute_import, division, print_function,\
                       unicode_literals
import sys
version = sys.version_info
python = version[0]


if python == 2:
    # Builtins
    import __builtin__ as builtins

    # Pickling
    import cPickle as picklemod

    class PickleCompat(object):
        def dump(self, obj, file):
            return picklemod.dump(obj, file, protocol=2)

        def load(self, file):
            return picklemod.load(file)
    pickle = PickleCompat()

    # Reloading
    reload = builtins.reload

    # Collections
    import collections
    collections.abc = collections

if python == 3:
    # Builtins
    import builtins

    # Pickling
    import pickle as picklemod

    class PickleCompat(object):
        def dump(self, obj, file):
            return picklemod.dump(obj, file, protocol=2, fix_imports=True)

        def load(self, file):
            try:
                return picklemod.load(file)
            except UnicodeDecodeError:
                file.seek(0)
                return picklemod.load(file, encoding='latin1')
    pickle = PickleCompat()

    # Reloading
    from importlib import reload

    # Collections
    import collections
