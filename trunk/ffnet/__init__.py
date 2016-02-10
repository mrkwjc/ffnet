########################################################################
## Copyright (C) 2006 by Marek Wojciechowski
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of LGPL-3.0 license
## https://opensource.org/licenses/LGPL-3.0
########################################################################
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
