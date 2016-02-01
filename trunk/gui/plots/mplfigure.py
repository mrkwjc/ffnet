#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'
from traits.api import *
from traitsui.api import *
from traits.etsconfig.api import ETSConfig
from matplotlib.figure import Figure
import matplotlib.animation as animation
from pyface.api import GUI
import collections
import sys
import pyface.api as pyface

if ETSConfig.toolkit == 'wx':
    from mplwx import MPLFigureEditor
if ETSConfig.toolkit == 'qt4':
    from mplqt import MPLFigureEditor

from mplconfig import BasicMPLFigureConfig


class MPLFigureHandler(Handler):
    def init(self, info):
        info.object._setup()
        return True


class MPLFigure(HasTraits):
    figure = Instance(Figure, ())
    config = Any

    def __init__(self, **traits):
        super(MPLFigure, self).__init__(**traits)
        self.axes = self.figure.add_subplot(111)
        self.figure.traited = self  # for callbacks in navigation toolbar

    def _setup(self):
        self.setup()

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
        self._setup()
        self.draw()

    def configure(self):
        if not self.config:
            BasicMPLFigureConfig(self).edit_traits(kind = 'livemodal')
            return
        self.config(self).edit_traits(kind = 'livemodal')


    view = View(UItem('figure', editor = MPLFigureEditor()),
                handler = MPLFigureHandler,
                resizable = True,
                width = 1024,
                height = 640)


#class MPLPlotter(HasTraits):
    #figure = Instance(MPLFigure)
    #live = Bool(True)

    #def __init__(self, **traits):
        #super(MPLPlotter, self).__init__(**traits)
        #self.figure = MPLFigureWithPlotter()
        #self.figure.plotter = self

    #@on_trait_change('+live', post_init=True)
    #def _plot(self, name, value):
        #if self.live and self.trait(name).live:
            #self.clear()
            #self.setup()
            #self.plot()
            #self.draw()

    ##def _setup(self):
        ##self.setup()

    #def clear(self):
        #self.figure.axes.clear()

    #def draw(self):
        #self.figure.draw()

    #def setup(self):  # Implement this for initial setup
        #pass

    #def plot(self):  # Implement this for real plots
        #pass

    #view = View(resizable = True)


class MPLPlotter(HasTraits):
    live = Bool(True)
    figure = Instance(MPLFigure)

    def __init__(self, **traits):
        self.figure = MPLFigureWithPlotter()  # First create figure
        self.figure.plotter = self
        super(MPLPlotter, self).__init__(**traits)  # Then initialize

    @on_trait_change('+live', post_init=True)
    def _replot(self, name, value):
        if self.live and self.trait(name).live:
            self.replot()

    def replot(self):
        self.figure.axes.clear()
        self.setup()
        self.plot_init()
        self.plot(self.plot_data())
        self.figure.draw()

    def relim(self):
        ax = self.figure.axes
        ax.relim()
        ax.autoscale_view()

    def setup(self):
        pass

    def plot_init(self):
        pass

    def plot_data(self):
        pass

    def plot(self, data = None):
        pass

    traits_view = View(resizable = True)

    figure_view = View(UItem('figure', style = 'custom'),
                             resizable = True,
                             width = 1024,
                             height = 640)


class MPLAnimator(MPLPlotter):
    interval = Int(100)
    repeat = Bool(False)
    blit = Bool(False)
    running = Bool(False)
    startstop = Button

    def animation_data(self):
        while self.running:
            yield self.plot_data()

    def start(self):
        if self.running:
            return  # Do not start again!
        self.running = True
        def tocall():
            self.animator = animation.FuncAnimation(self.figure.figure,
                                                    self.plot,
                                                    frames = self.animation_data,
                                                    init_func = self.plot_init,
                                                    interval = self.interval,
                                                    blit = self.blit,
                                                    repeat = self.repeat)
            self.animator._start()
        GUI.invoke_later(tocall)

    def stop(self):
        if not self.running:
            return  # Do not stop when we are not running
        self.running = False
        def tocall():
            self.animator._stop()
            self.figure.figure.canvas.toolbar.update()
        GUI.invoke_later(tocall)

    def _startstop_fired(self):
        if not self.running:
            self.start()
        else:
            self.stop()

    traits_view = View(UItem('startstop', label = 'Start/Stop'),
                       resizable = True)

    figure_view = View(UItem('figure', style = 'custom'),
                             resizable = True,
                             width = 1024,
                             height = 640)


class MPLFigureWithPlotter(MPLFigure):
    plotter = Instance(MPLPlotter)
    plotter_width = 0.35

    def _setup(self):
        self.setup()
        if self.plotter is not None:
            self.plotter.setup()

    def default_traits_view(self):
        width = self.plotter_width
        if self.plotter is None:
            width = 0.0
        return View(HSplit(UItem('figure', editor = MPLFigureEditor()),
                           UItem('plotter', style = 'custom', width = width)),
                    handler = MPLFigureHandler,
                    resizable = True,
                    width = 1024,
                    height = 640
                    )


if __name__=="__main__":
    p = MPLAnimator()
    p.configure_traits(view='figure_view')
