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
from traits.etsconfig.api import ETSConfig
if ETSConfig.toolkit == 'wx':
    from mplwx import MPLFigureEditor
if ETSConfig.toolkit == 'qt4':
    from mplqt import MPLFigureEditor
from mplconfig import BasicMPLFigureConfig
from matplotlib.figure import Figure
import matplotlib.animation as animation
from pyface.api import GUI
import time


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

    def _flush_events(self):
        try:
            self.figure.canvas.flush_events()
        except:
            pass

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

    def replot2(self):
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
        self.animator = animation.FuncAnimation(self.figure.figure,
                                                self.plot,
                                                frames = self.animation_data,
                                                init_func = self.plot_init,
                                                interval = self.interval,
                                                blit = self.blit,
                                                repeat = self.repeat)
        try:
            self.animator._start()
        except:
            pass

    def stop(self):
        if not self.running:
            return  # Do not stop when we are not running
        self.running = False
        try:
            self.animator._stop()
        except:
            pass
        self.figure.figure.canvas.toolbar.update()

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


class MPLPlots(HasTraits):
    classes = List([])
    names = Property(ListStr, depends_on='classes', transient=True)
    selected_name = Enum(values='names', transient=True)
    selected = Instance(MPLPlotter)
    plots = List([], value=MPLPlotter)
    running = Bool(False)
    interval = Int(250)

    def __init__(self, **traits):
        super(MPLPlots, self).__init__(**traits)
         # Hack for displaying initial state with configure_traits
        self.classes = [MPLPlotter]
        self.classes = []

    def _get_names(self):
        names = []
        for i, c in enumerate(self.classes):
            if hasattr(c, 'name'):  # in case name is just python type
                name = c.name
            elif 'name' in c.class_traits():
                name = c.class_traits()['name'].default  # in case 'name' is a trait
            else:
                name = 'Plot %i' %i
            names.append(name)
        return names

    def _classes_changed(self):
        self.plots = []
        names = self._get_names()
        if len(names) > 0:
            self.selected_name = names[0]
            self.load_plot(names[0])  # Force plot loading

    @on_trait_change('selected_name')
    def load_plot(self, name):
        idx = self.names.index(name)
        cls = self.classes[idx]
        for plot in self.plots:
            if plot.__class__ == cls:
                break
        else:
            plot = cls()
            self.plots.append(plot)
        # Show new plot
        if self.running:
            self.stop()
            self.selected = plot
            self.selected.replot()
            self.start()
        else:
            self.selected = plot
            self.selected.replot()

    def replot(self):
        t0 = time.time()
        self.selected.replot()
        t1 = time.time()
        self.interval = int(max(250, 2*1000*(t1-t0)))

    def start(self):
        if self.selected:
            if isinstance(self.selected, MPLAnimator):
                self.selected.interval = self.interval
                self.selected.start()
            self.running = True

    def stop(self):
        if self.selected:
            if isinstance(self.selected, MPLAnimator):
                self.selected.stop()
            self.selected.replot2()
            self.running = False

    traits_view = View(UItem('selected_name'),
                       UItem('object.selected.figure',
                             style='custom',
                             visible_when='len(plots)>0'),
                       resizable = True)


if __name__=="__main__":
    p = MPLPlots()
    p.configure_traits(view='traits_view')
