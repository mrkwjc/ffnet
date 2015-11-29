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
