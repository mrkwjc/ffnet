python setup.py sdist
python setup.py build --compiler=mingw32
python setup.py bdist --skip-build
python setup.py bdist_wininst --skip-build
python setup.py bdist_wheel --skip-build

REM conda install setuptools mingw
REM pip install --user --upgrade --global-option="build" --global-option="--compiler=mingw32" ffnet

REM ~ python setup.py bdist_wininst

REM ~ python setup.py sdist register upload
REM ~ python setup.py bdist_wininst register upload

REM ~ python setup.py build --compiler=mingw32
REM ~ python setup.py bdist_wininst --skip-build
REM ~ python setup.py sdist

REM c:\Anaconda\envs\py34\python.exe setup.py build --compiler=mingw32
REM c:\Anaconda\envs\py34\python.exe setup.py bdist_wininst --skip-build

REM c:\Anaconda\envs\py33\python.exe setup.py build --compiler=mingw32
REM c:\Anaconda\envs\py33\python.exe setup.py bdist_wininst --skip-build

REM c:\Anaconda\envs\py26\python.exe setup.py build --compiler=mingw32
REM c:\Anaconda\envs\py26\python.exe setup.py bdist_wininst --skip-build