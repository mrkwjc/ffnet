from PyInstaller.utils.hooks import collect_data_files

# Necessary by networkx-1.10
hiddenimports = ['lib2to3'] 
datas = collect_data_files('lib2to3')
