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

from __future__ import absolute_import
from ._version import version
import ffnet.fortran as fortran
import ffnet.ffnet as ffnetmodule
from ffnet.ffnet import ffnet, \
                  mlgraph, \
                  tmlgraph, \
                  imlgraph, \
                  savenet, \
                  loadnet, \
                  exportnet, \
                  readdata
from ffnet.pikaia import pikaia
import ffnet._tests as _tests
