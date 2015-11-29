#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'
from traits.api import *
from traitsui.api import *
from mplfigure import MPLPlotter
import numpy as np

class ErrorPlot(MPLPlotter):
    training_error = CArray(live = True)
    validation_error = CArray(live = True)
    step = Int(1, live = True)
    show_validation_error = Bool(True, live = True)
    show_training_error = Bool(True, live = True)
    _training_progress = Range(0, 99)
    is_training = Bool(False)

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

    def _is_training_changed(self):
        self._training_progress = 0
        import thread, time
        def torun():
            while self.is_training:
                for j in range(99):
                    if self.is_training:
                        self._training_progress += 1
                        time.sleep(0.05)
                    else:
                        break
                self._training_progress = 0
        if self.is_training:
            thread.start_new_thread(torun, ())


    view = View(Item('show_training_error', label = "Training error"),
                Item('show_validation_error', label = "Validation error"),
                Group(UItem('_training_progress',
                            editor = ProgressEditor(message = 'Training',
                                                    min = 0,
                                                    max = 100),
                            visible_when = 'is_training')),
                resizable = True)

if __name__ == "__main__":
    p = ErrorPlot()
    p.training_error = np.random.rand(50)
    p.validation_error = np.random.rand(50)
    p.figure.configure_traits()