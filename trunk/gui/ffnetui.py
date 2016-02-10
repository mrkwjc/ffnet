#!/usr/bin/env python
#-*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

## Look for available toolkits - prefer 'wx'
from traits.etsconfig.api import ETSConfig
try:
    import wx
    if wx.VERSION[0] == 2 and wx.VERSION[1] == 8:
        ETSConfig.toolkit = 'wx'
    else:
        raise ImportError
except ImportError:
    try:
        import PySide
        ETSConfig.toolkit = 'qt4'
    except ImportError:
        import PyQt4
        ETSConfig.toolkit = 'qt4'
    else:
        raise ImportError('Neither "wx (2.8)" nor "qt4" backends are available.')

## Define main functions
from ffnetapp import FFnetApp

def main():
    app = FFnetApp()
    app.configure_traits()
    return app

def test():
    app = FFnetApp()
    # Add test network
    from ffnet import loadnet
    n = app.network
    path = 'data/testnet.net'
    n.net = loadnet(path)
    n.filename = path
    ## Add test data
    app.data.input_loader.filename = 'data/black-scholes-input.dat'
    app.data.target_loader.filename = 'data/black-scholes-target.dat'
    app.data.load()
    app.mode = 'train'
    app._arrange_plots()
    # Run
    app.configure_traits()
    return app

if __name__=="__main__":
    import multiprocessing as mp
    mp.freeze_support()
    app = main()
    #app = test()
