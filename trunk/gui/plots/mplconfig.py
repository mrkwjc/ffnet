# -*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

# from traits.etsconfig.api import ETSConfig
# ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *

class MPLFigureConfigHandler(Handler):
    def apply(self, info):
        info.object.setvals()

class MPLFigureConfig(HasTraits):
    figure = Any

class BasicMPLFigureConfig(MPLFigureConfig):
    title = Str
    xlabel = Str
    ylabel = Str
    grid = Bool(False)
    xscale = Enum('linear', 'log', 'symlog')
    yscale = Enum('linear', 'log', 'symlog')
    aspect = Enum('auto', 'equal', 'num')
    aspect_value = Float(1.)
    show_legend = Bool(False)
    edit_legend = Bool(False)
    legend = List(Str)

    def __init__(self, figure, **traits):
        self.figure = figure
        self.getvals()
        super(BasicMPLFigureConfig, self).__init__(**traits)

    def getvals(self):  # should be run only on init!
        self.title = self.figure.axes.get_title()
        self.xlabel = self.figure.axes.get_xlabel()
        self.ylabel = self.figure.axes.get_ylabel()
        self.grid = self.figure.axes.xaxis._gridOnMajor  # is better way?
        self.xscale = self.figure.axes.get_xscale()
        self.yscale = self.figure.axes.get_yscale()
        self.aspect = self._get_aspect()
        self.legend = self._get_line_labels()
        self.show_legend = True if self.figure.axes.legend_ is not None else False

    def setvals(self):
        self.figure.axes.set_title(self.title)
        self.figure.axes.set_xlabel(self.xlabel)
        self.figure.axes.set_ylabel(self.ylabel)
        self.figure.axes.grid(self.grid)
        self.figure.axes.set_xscale(self.xscale)
        self.figure.axes.set_yscale(self.yscale)
        self._set_aspect(self.aspect)
        self._set_line_labels(self.legend)

    @on_trait_change('anytrait', post_init=True)
    def _setvals(self):
        self.setvals()
        self.figure.draw()

    def _get_aspect(self):
        aspect = self.figure.axes.get_aspect()
        if isinstance(aspect, float):
            self.aspect_value = aspect
            aspect = 'num'
        return aspect

    def _set_aspect(self, aspect):
        if aspect == 'num':
            aspect = self.aspect_value
        self.figure.axes.set_aspect(aspect)

    def _get_line_labels(self):
        labels = []
        for line in self.figure.axes.lines:
            l = line.get_label()
            labels.append(l)
        return labels

    def _set_line_labels(self, labels):
        for line, l in zip(self.figure.axes.lines, labels):
            line.set_label(l)
        if self.show_legend:
            self.figure.axes.legend(loc='best')
        else:
            self.figure.axes.legend_ = None

    basic_config_group = \
        Group(Item('title', editor=TextEditor(auto_set=False)),
              Item('xlabel', editor=TextEditor(auto_set=False)),
              Item('ylabel', editor=TextEditor(auto_set=False)),
              Item('xscale'),
              Item('yscale'),
              Item('grid'),
              HGroup(Item('aspect'), Item('aspect_value', visible_when = 'aspect == "num"')),
              HGroup(Item('show_legend', visible_when = 'object.figure.axes.lines'),
              Item('edit_legend', visible_when = 'object.figure.axes.lines and show_legend')),
              Item('legend',
                    editor = ListEditor(mutable = False, editor=TextEditor(auto_set=False)),
                    visible_when = 'show_legend and edit_legend'),
              show_border = True)

    traits_view = View(basic_config_group,
                       buttons = ['Apply', 'OK', 'Cancel'],
                       handler = MPLFigureConfigHandler(),
                       title = 'Graph configuration',
                       width = 0.25,
                       resizable = True)

if __name__=="__main__":
    from mplfigure import MPLFigure
    import numpy as np
    p = MPLFigure()
    p.axes.plot(np.random.rand(200), 'bo-', ms=6.)
    p.axes.plot(np.random.rand(200), 'rs-', ms=6.)
    p.axes.legend()
    p.configure_traits()