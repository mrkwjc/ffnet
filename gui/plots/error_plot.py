#-*- coding: utf-8 -*-
##from traits.etsconfig.api import ETSConfig
##ETSConfig.toolkit = 'qt4'
from traits.api import *
from traitsui.api import *
from mplfigure import MPLPlotter
from progress import * # ProgressInfiniteWaiter
import numpy as np

class ErrorPlot(MPLPlotter):
    training_error = CArray(live = True)
    validation_error = CArray(live = True)
    step = Int(1, live = True)
    show_validation_error = Bool(True, live = True)
    show_training_error = Bool(True, live = True)
    training_in_progress = Instance(ProgressInfiniteWaiter, ())
    is_running = DelegatesTo('training_in_progress')

    def setup(self):
        ax = self.figure.axes
        ax.set_yscale("log")
        ax.grid(True)

    def plot(self):
        ax = self.figure.axes
        terr = self.training_error
        verr = self.validation_error
        if len(terr) == 0:
            return
        if self.show_training_error:
            n = len(terr)
            iterations = np.arange(0, n, self.step)
            ax.plot(iterations, terr, 'ro-', lw=2, label='Training error')
        if len(verr) > 0 and self.show_validation_error:
            n = len(verr)
            iterations = np.arange(0, n, self.step)
            ax.plot(iterations, verr, 'gv-', lw=2, label='Validation error')
        ax.set_yscale("log")
        ax.grid(True)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('$\sum_i\sum_j\left(o_{ij} - t_{ij}\\right)^2$')
        ax.legend(loc='best')


    view = View(Item('show_training_error', label = "Training error"),
                Item('show_validation_error', label = "Validation error"),
                Group(Item('training_in_progress', style='custom', visible_when = 'is_running')),
                resizable = True)

if __name__ == "__main__":
    p = ErrorPlot()
    p.training_error = np.random.rand(50)
    p.validation_error = np.random.rand(50)
    p.figure.configure_traits()