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

def test():
   ''' Runs test suite for ffnet modules '''
   import tests, unittest
   suite = unittest.TestLoader().loadTestsFromModule(tests)
   unittest.TextTestRunner(verbosity=2).run(suite)