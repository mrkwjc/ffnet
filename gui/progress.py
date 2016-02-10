#-*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *


class TxtInfiniteWaiter(HasTraits):
    _progress = Str
    _sequence = List(Str)
    _speed = Float
    length = Int(20)
    msg = Str('---')
    speed = Float(2.0)
    is_running = Bool(False)

    def __init__(self, msg = '---', length = 20, speed = 1.0, **traits):
        super(TxtInfiniteWaiter, self).__init__(**traits)
        self.msg = msg
        self.length = length
        self.speed = speed
        self._compute_sequence()
        self._compute_speed()

    @on_trait_change('length, msg')
    def _compute_sequence(self):
        N = self.length
        n = len(self.msg)
        assert N > n
        base = self.msg
        sequence = []
        for i in range(N-n+1):
            s = '[' + ' '*i + base + ' '*(N-n-i) + ']'
            sequence.append(s)
        sequence += reversed(sequence[1:-1])
        self._sequence = sequence

    @on_trait_change('length, msg, speed')
    def _compute_speed(self):
        N = self.length
        n = len(self.msg)
        self._speed = self.speed/(N-n)

    def _is_running_changed(self):
        self._progress = ''
        import thread, time
        def torun():
            while self.is_running:
                for i in range(len(self._sequence)):
                    if self.is_running:
                        try:
                            self._progress = self._sequence[i]
                        except IndexError:  # length of sequence could change...
                            break
                        time.sleep(self._speed)
                    else:
                        break
        if self.is_running:
            thread.start_new_thread(torun, ())

    view = View(UItem('_progress', style = 'readonly', emphasized=True),
                resizable = True, width = 0.2)


class ProgressInfiniteWaiter(HasTraits):
    _progress = Range(0, 100)
    speed = Float(5.0)
    is_running = Bool(False)

    def __init__(self, speed = 5.0, **traits):
        super(ProgressInfiniteWaiter, self).__init__(**traits)
        self.speed = speed

    def _is_running_changed(self):
        self._progress = 0
        import thread, time
        def torun():
            while self.is_running:
                for j in range(99):
                    if self.is_running:
                        self._progress += 1
                        time.sleep(self.speed/100.)
                    else:
                        break
                self._progress = 0
        if self.is_running:
            thread.start_new_thread(torun, ())

    view = View(UItem('_progress', editor = ProgressEditor(min = 0, max = 100)),
                resizable = True, width = 0.2)

if __name__ == "__main__":
    p = TxtInfiniteWaiter()
    p.is_running = True
    p.configure_traits()
    p1 = ProgressInfiniteWaiter()
    p1.is_running = True
    p1.configure_traits()
    