#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'
from traits.api import *
from traitsui.api import *
from mplfigure import MPLAnimator
import numpy as np
import multiprocessing as mp

class ErrorAnimation(MPLAnimator):
    relative_error = Bool(False)

    def __init__(self, app=None, **traits):
        super(ErrorAnimation, self).__init__(**traits)
        self.app = app

    def plot_init(self):
        self.figure.axes.clear()
        ax = self.figure.axes
        self.tline, = ax.plot([], [], 'ro-', lw=2, label='Training error')
        self.vline, = ax.plot([], [], 'gv-', lw=2, label='Validation error')
        ax.set_yscale("log")
        ax.grid(True)
        ax.set_xlabel('Iteration')
        #ax.set_ylabel('$\sum_i\sum_j\left(o_{ij} - t_{ij}\\right)^2$')
        ax.set_ylabel('Error')
        ax.legend(loc='best')
        return self.tline, self.vline

    def plot_data(self):
        while self.running:
            it = self.app.shared.ilist
            terr = self.app.shared.tlist
            verr = self.app.shared.vlist
            if self.relative_error:
                terr = [t/terr[0] for t in terr]
                verr = [v/verr[0] for v in verr]
            if len(verr) > 0:
                n = min(len(it), len(terr), len(verr))  # instead of synchronization
            else:
                n = min(len(it), len(terr))
            yield it[:n], terr[:n], verr[:n]

    def plot(self, data):
        it, terr, verr = data
        ax = self.figure.axes
        self.tline.set_data(it, terr)
        if len(verr) > 0:
            self.vline.set_data(it, verr)
        self.relim()
        return self.tline, self.vline

    #def relim(self):
        #ax = self.figure.axes
        #ax.relim()
        #ax.autoscale_view()
        #xl, xh = ax.get_xlim()
        #xh = (1 + len(self.iterations)//50) * 50
        #ax.set_xlim((xl, xh))
        #ax.autoscale_view()

    traits_view = View(Item('relative_error'),
                            resizable = True)

    #traits_view = View(Item('startstop', label='Start/Stop'),
                          #Item('relative_error'),
                          #resizable = True)


if __name__ == "__main__":
    p = ErrorAnimation()
    p.interval = 100
    import thread, threading
    import time
    lock = threading.Lock()
    def generate_data(p):
        time.sleep(0.1)
        for i in range(300):
            t = np.arange(0, 0.05*i, 0.05)
            terr = np.sin(2*np.pi*t) * np.exp(-t/10.)
            verr = np.sin(2*np.pi*t) * np.exp(-t/10.)/2.
            lock.acquire()
            p.training_error = terr
            p.validation_error = verr
            p.iterations = t*20
            lock.release()
            time.sleep(0.05)
        p.stop()
    thread.start_new_thread(generate_data, (p,))
    p.figure.configure_traits()
    p.start() # this will work only with ipython --gui=wx
