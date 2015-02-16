.. _apidoc:

.. default-role:: py:obj

.. currentmodule:: ffnet

--------
API docs
--------

The list below summarizes classes and functions exposed to the user, ie. imported by::

    from ffnet import *

.. currentmodule:: ffnet
.. autosummary::
    ffnet
    mlgraph
    tmlgraph
    imlgraph
    savenet
    loadnet
    exportnet
    readdata

.. currentmodule:: pikaia
.. autosummary::
    pikaia

.. currentmodule:: ffnet

Architecture generators
-----------------------
.. autofunction:: mlgraph
.. autofunction:: tmlgraph
.. autofunction:: imlgraph

Main ffnet class
----------------
.. autoclass:: ffnet.ffnet
    :members:

Utility functions
-----------------
.. autofunction:: savenet
.. autofunction:: loadnet
.. autofunction:: exportnet
.. autofunction:: readdata

.. currentmodule:: pikaia

Pikaia optimizer
----------------
.. autofunction:: pikaia
