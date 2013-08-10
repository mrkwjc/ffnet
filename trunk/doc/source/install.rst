-------------
Getting ffnet
-------------

Requirements
^^^^^^^^^^^^

At run time...
++++++++++++++
ffnet needs at least:

* `python-2.6 <http://python.org>`_ (or 2.4, 2.5 + multiprocessing), python-3.x is not supported yet
* `numpy-1.4 <http://numpy.org>`_
* `scipy-0.8 <http://scipy.org>`_
* `networkx-1.3 <http://networkx.lanl.gov>`_

For plots (which appear in examples) you'll need the `matplotlib <http://matplotlib.sourceforge.net>`_ package. It is also very convenient to use ffnet interactively with `ipython <http://ipython.scipy.org/moin>`_, an enhanced python shell.


At compilation time...
++++++++++++++++++++++
ffnet uses numpy.distutils and f2py tool (shipped with numpy) to compile Fortran parts of the library. If you're going to compile ffnet from sources (actually you have to do so unless your OS does not provide binary package) you'll need also:

* Python header files (which are installed with Python by default on Windows, but not on most Linux distros, for example on Ubuntu you need additional ``python-dev`` package),
* C and Fortran 77 compilers (on Linux you have gcc and gfortran, on Windows (32-bit) you can consider using `mingw32 <http://sourceforge.net/projects/mingw/files/Installer/mingw-get-inst/>`_).


You might also be interested in installing `Enthought Python Distribution <http://www.enthought.com/products/epd_free.php>`_ which reaches all ffnet requirements (including compilers) and is free for non-commercial use.

Download
^^^^^^^^
Go to sourceforge `download page <http://sourceforge.net/projects/ffnet/files/ffnet>`_ for release versions of ffnet.

You can also checkout development version of the code from the project subversion repository:

    ``svn co https://svn.code.sf.net/p/ffnet/code/trunk ffnet``

or from this direct `link <http://ffnet.svn.sourceforge.net/viewvc/ffnet/trunk.tar.gz>`_.


Installation
^^^^^^^^^^^^
If you have `setuptools <http://pypi.python.org/pypi/setuptools>`_ installed you can try to call from command line (as root):

    ``easy_install ffnet``

Alternatively, if you have `pip <http://pypi.python.org/pypi/pip>`_, you can call:

    ``pip install ffnet``

These commands should automatically download, compile and install ffnet.

If this doesn't work for you, try manual installation. Unpack ffnet to the directory of your choice, enter it and run:

* on Linux (gcc + gfortran):
    ``python setup.py install``

* on Windows (mingw32: gcc + g77):
    ``python setup.py build --compiler=mingw32 & python setup.py install --skip-build``

You are also welcome to produce and share binary packages for your operating system. They will be placed at ffnet's `download page`_.


Testing
^^^^^^^
Installation can be tested in python console::

    from ffnet._tests import runtest
    runtest()

Remember to leave installation directory first!

Execute also ffnet examples. They all should work.

