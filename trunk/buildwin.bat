python setup.py build --compiler=mingw32
python setup.py bdist_wininst --skip-build
python setup.py sdist

REM c:\Anaconda\envs\py34\python.exe setup.py build --compiler=mingw32
REM c:\Anaconda\envs\py34\python.exe setup.py bdist_wininst --skip-build

REM c:\Anaconda\envs\py33\python.exe setup.py build --compiler=mingw32
REM c:\Anaconda\envs\py33\python.exe setup.py bdist_wininst --skip-build

REM c:\Anaconda\envs\py26\python.exe setup.py build --compiler=mingw32
REM c:\Anaconda\envs\py26\python.exe setup.py bdist_wininst --skip-build