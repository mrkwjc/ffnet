#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *
from plots.mplfigure import MPLAnimator
import numpy as np


class ErrorAnimation(MPLAnimator):
    name = Str('Training error')
    app = Any
    relative_error = Bool(False)

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
        return it[:n], terr[:n], verr[:n]

    def plot(self, data=None):
        it, terr, verr = data if data is not None else self.plot_data()
        ax = self.figure.axes
        self.tline.set_data(it, terr)
        if len(verr) > 0:
            self.vline.set_data(it, verr)
        self.relim()
        return self.tline, self.vline

    traits_view = View(Item('relative_error'),
                            resizable = True)


class TOAnimation(MPLAnimator):
    name = Str('Target vs. Output')
    app = Any
    outputs = Property(List, depends_on='app.network.net')
    output = Enum(values='outputs')

    def _get_outputs(self):
        if self.app is not None and self.app.network.net is not None:
            return range(len(self.app.network.net.outno))
        return []

    def plot_init(self):
        self.figure.axes.clear()
        ax = self.figure.axes
        self.tline, = ax.plot([], [], 'og', label='Training data')
        self.vline, = ax.plot([], [], 'or', label='Validation data')
        self.rline, = ax.plot([], [], 'k', lw=2, label='Regression line')
        ax.grid(True)
        ax.set_xlabel('Targets')
        ax.set_ylabel('Outputs')
        ax.legend(loc='best')
        return self.tline, self.vline, self.rline

    def plot_data(self):
        i = self.app.data.input
        t = self.app.data.target
        vmask = self.app.data.vmask
        o, r = self.app.network.net.test(i, t, iprint = 0)
        slope = r[0][0]
        intercept = r[0][1]
        offset = (t.max() - t.min())*0.05
        x = np.linspace(t.min()-offset, t.max()+offset)
        y = slope * x + intercept
        tt = t[~vmask][:, self.output]
        tv = t[vmask][:, self.output]
        ot = o[~vmask][:, self.output]
        ov = o[vmask][:, self.output]
        return tt, ot, tv, ov, x, y

    def animation_data(self):
        while self.running:
            self.app.network.net.weights[:] = self.app.shared.wlist[-1]
            yield self.plot_data()

    def plot(self, data=None):
        tt, ot, tv, ov, x, y = data if data is not None else self.plot_data()
        ax = self.figure.axes
        self.tline.set_data(tt, ot)
        self.vline.set_data(tv, ov)
        self.rline.set_data(x, y)
        self.relim()
        return self.tline, self.vline, self.rline


    traits_view = View(Item('output'),
                            resizable = True)


class Plots(HasTraits):
    app = Any
    plist = List([ErrorAnimation(), TOAnimation()])
    selected = Any

    def _app_changed(self):
        for p in self.plist:
            p.app = self.app

    def _selected_changed(self, old, new):
        if self.app is not None:
            if self.app.trainer.running:
                try:
                    # Assume we have animation
                    old.stop()
                except:
                    # But simple plot can be also
                    pass
                try:
                    # Assume we have animation
                    new.start()
                except:
                    # But simple plot can be also
                    new.plot()
            else:
                new.plot_init()
                new.plot()

    traits_view = View(Item('plist',
                            style='custom',
                            show_label=False,
                            editor=ListEditor(use_notebook=True,
                                              deletable=False,
                                              dock_style='tab',
                                              selected='selected',
                                              view = 'figure_view',
                                              page_name = '.name')),
                       resizable = True,
                       width = 1024,
                       height = 640)


if __name__ == "__main__":
    p = Plots()
    p.configure_traits()
