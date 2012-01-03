"""
-------------
ffnet package
-------------
"""

from _version import version
import fortran
import ffnet as ffnetmodule
from ffnet import ffnet, \
                  mlgraph, \
                  tmlgraph, \
                  imlgraph, \
                  savenet, \
                  loadnet, \
                  exportnet, \
                  readdata
from pikaia import pikaia
import _tests
