#-*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

from traits.api import *
from traitsui.api import *
import multiprocessing as mp
from multiprocessing.managers import SyncManager

class Shared(HasTraits):
    manager = Instance(SyncManager, transient = True)

    def __init__(self, ncpu=1):
        self.manager = mp.Manager()
        self.populate()

    def populate(self):
        self.running = self.manager.Value('i', 0)
        self.iteration = self.manager.Value('i', 0)
        self.bwidx = self.manager.Value('i', 0)
        self.wlist = self.manager.list([])
        self.tlist = self.manager.list([])
        self.vlist = self.manager.list([])
        self.ilist = self.manager.list([])

    def bweights(self):
        return self.wlist[self.bwidx.value]


if __name__ == "__main__":
    s = Shared()
    def func(s):
        s.value = 1
        s.running.value = 1
    p = mp.Process(target=func, args=(s,))
    p.start()
    p.join()
    print s.running.value == 1
    print hasattr(s, 'value')