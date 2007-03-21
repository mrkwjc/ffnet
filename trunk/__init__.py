# ffnet package initialization

from _version import version
import fortran
import tools
from ffnet import ffnet, \
                  mlgraph, \
                  tmlgraph, \
                  imlgraph, \
                  savenet, \
                  loadnet, \
                  exportnet
from pikaia import pikaia

from _tests import runtest as test
