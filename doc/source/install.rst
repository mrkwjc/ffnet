------------
Installation
------------

Requirements
^^^^^^^^^^^^

**ffnet** needs at least:

* `python-2.6 <http://python.org>`_ (or 2.4, 2.5 + multiprocessing), python-3.x is also supported
* `numpy-1.4 <http://numpy.org>`_
* `scipy-0.8 <http://scipy.org>`_
* `networkx-1.3 <http://networkx.lanl.gov>`_

**ffnetui** depends additionally on:

* `matplotlib <http://matplotlib.sourceforge.net>`_
* `traitsui <http://code.enthought.com/projects/traits_ui/>`_

For **ffnetui** python-2.7 is necessary. This is because traitsui does not work well with python-3.x currently.

If you're going to compile ffnet from sources you'll need also:

* Python header files (which are installed with Python by default on Windows, but not on most Linux distros, for example on Ubuntu you need additional ``python-dev`` package),
* C and Fortran 77 compilers (on Linux you have gcc and gfortran, on Windows you can consider using `mingw32 <http://sourceforge.net/projects/mingw/files/Installer/mingw-get-inst/>`_).

On Windows you can conveniently install `Python(xy) <https://code.google.com/p/pythonxy>`_ distribution which comes now with ffnet (and its dependencies) preinstalled. Also, you might be interested in installing `Anaconda <https://store.continuum.io/cshop/anaconda/>`_ which reaches all ffnet requirements (including compilers) and is free for non-commercial use.

Installation on Linux
^^^^^^^^^^^^^^^^^^^^^
Just call from command line:

    ``pip install ffnet``

    ``pip install ffnetui``

or unpack downloaded `tar.gz <http://sourceforge.net/projects/ffnet/files/ffnet/0.8.3>`_ files and run:

    ``python setup.py install``

The first method will install also dependencies, the second one probably will not.

If you get compilation errors then you possibly need *gcc* and *gfortran* and/or python headers.

Installation on Windows
^^^^^^^^^^^^^^^^^^^^^^^
If you have proper system setup the above methods should also work. However you can try binary installers available on `download page <http://sourceforge.net/projects/ffnet/files/ffnet/0.8.3>`_. Be aware, that installers for **ffnet** need working python installation and do not check dependencies. On the other hand **ffnetui** installers are all-in-one, self-contained bundles. You don't even need python to install and use ffnetui.


Testing
^^^^^^^
ffnet installation can be tested in python console::

    from ffnet._tests import runtest
    runtest()

Remember to leave installation directory first!

Execute also ffnet examples. They all should work.

