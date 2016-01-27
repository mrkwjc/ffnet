from PyInstaller.utils.hooks import collect_data_files

hiddenimports = ['lib2to3'] 
datas = collect_data_files('lib2to3')
