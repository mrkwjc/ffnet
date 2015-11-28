#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'
from traits.api import *
from traitsui.api import *
from traits.etsconfig.api import ETSConfig
from matplotlib.figure import Figure
from pyface.api import GUI
import collections
import sys
import pyface.api as pyface

if ETSConfig.toolkit == 'wx':
    from mplwx import MPLFigureEditor
if ETSConfig.toolkit == 'qt4':
    from mplqt import MPLFigureEditor

from mplconfig import BasicMPLFigureConfig

class MPLPlotter(HasTraits):
    figure = Any

    def __init__(self, **traits):
        super(MPLPlotter, self).__init__(**traits)
        self.figure = MPLFigure()
        self.figure.plotter = self

    @on_trait_change('+live')
    def _plot(self):
        self.clear()
        self.setup()
        self.plot()
        self.draw()

    def _setup(self):
        self.setup()

    def clear(self):
        self.figure.axes.clear()

    def draw(self):
        self.figure.draw()

    def setup(self):  # Implement this for initial setup
        pass

    def plot(self):  # Implement this for real plots
        pass


class MPLFigureHandler(Handler):
    def init(self, info):
        info.object._setup()
        return True


class MPLFigure(HasTraits):
    figure = Instance(Figure, ())
    config = Any
    plotter = Instance(MPLPlotter)

    def __init__(self, **traits):
        super(MPLFigure, self).__init__(**traits)
        self.axes = self.figure.add_subplot(111)
        self.figure.traited = self  # for callbacks in navigation toolbar

    def _setup(self):
        self.setup()
        if self.plotter is not None:
            self.plotter.setup()

    def _draw(self):
        try:
            self.figure.canvas.draw()
        except:
            pass
            #e = sys.exc_info()[1]
            #pyface.error(None, "Error when drawing figure!\n\n" + e.message)

    def _flush_events(self):
        try:
            self.figure.canvas.flush_events()
        except:
            pass
            #e = sys.exc_info()[1]
            #pyface.error(None, "Error when drawing figure!\n\n" + e.message)

    def setup(self):
        pass

    def draw(self):
        GUI.invoke_later(self._draw)
        GUI.invoke_later(self._flush_events)

    def reset(self):
        self.axes.clear()
        self.setup()
        self.draw()

    def configure(self):
        if not self.config:
            BasicMPLFigureConfig(self).edit_traits(kind = 'livemodal')
            return
        self.config(self).edit_traits(kind = 'livemodal')

    plotter_width = 0.4
    def default_traits_view(self):
        if self.plotter is None:
            self.plotter_width = 0.0
        return View(HSplit(UItem('figure', editor = MPLFigureEditor()),
                           UItem('plotter', style = 'custom', width = self.plotter_width)),
                    handler = MPLFigureHandler,
                    resizable = True,
                    width = 1024,
                    height = 640
                    )

if __name__=="__main__":
    p = MPLFigure()
    p.configure_traits()
