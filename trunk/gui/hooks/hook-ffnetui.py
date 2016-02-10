from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
import traitsui.api
from traits.etsconfig.api import ETSConfig
toolkit = ETSConfig.toolkit

hiddenimports = []
datas = []

if toolkit == 'wx':
    hiddenimports += collect_submodules('pyface.ui.wx')
    hiddenimports += collect_submodules('traitsui.wx')
    datas += collect_data_files('traitsui.image')
    datas += collect_data_files('traitsui.wx')
    datas += collect_data_files('pyface', subdir='images')
    datas += collect_data_files('pyface.ui.wx')
    datas += collect_data_files('pyface.dock')
elif toolkit == 'qt4':
    hiddenimports += collect_submodules('pyface.ui.qt4')
    hiddenimports += collect_submodules('traitsui.qt4')
    datas += collect_data_files('traitsui.image')
    datas += collect_data_files('traitsui.qt4')
    datas += collect_data_files('pyface', subdir='images')
    datas += collect_data_files('pyface.ui.qt4')
    datas += collect_data_files('pyface.dock')
else:
    pass

datas += [('./images/*.*',  'images')]
datas += [('./plots/images/*.*',  'plots/images')]
datas += [('./data/*',  'data')] 