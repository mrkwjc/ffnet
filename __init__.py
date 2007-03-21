# ffnet package initialization

from version import version
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

from tests import runtest as test
try: del tests
except: pass
