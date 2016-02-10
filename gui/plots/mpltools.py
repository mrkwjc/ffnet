# -*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

import matplotlib

def hexcolor(color):
    """
    Convert wx or qt colors to hex string used by matplotlib.
    """
    if 'wx' in str(color.__class__):
        rgba = color.Get(includeAlpha=True)
    elif 'Qt' in str(color.__class__):
        rgba = color.getRgb()
    else:
        rgba = color
    mplrgba = [float(item)/255 for item in rgba]
    return matplotlib.colors.rgb2hex(tuple(mplrgba))
