from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files

hiddenimports = []
hiddenimports += collect_submodules('pyface.ui.wx')
hiddenimports += collect_submodules('traitsui.wx')

datas = []
datas += collect_data_files('traitsui.image')
datas += collect_data_files('traitsui.wx')
datas += collect_data_files('pyface', subdir='images')
datas += collect_data_files('pyface.ui.wx')
datas += collect_data_files('pyface.dock')
datas += [('C:\\Documents and Settings\\mwojc\\pyapps\\ffnet\\gui\\images\\*.png',  'images')]
datas += [('C:\\Documents and Settings\\mwojc\\pyapps\\ffnet\\gui\\plots\\images\\*.png',  'plots\\images')]
datas += [('C:\\Documents and Settings\\mwojc\\pyapps\\ffnet\\gui\\data\\*',  'data')]