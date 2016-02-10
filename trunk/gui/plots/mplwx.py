# -*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

import wx
import matplotlib
# We want matplotlib to use a wxPython backend
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg
from traitsui.wx.editor import Editor
from traitsui.wx.basic_editor_factory import BasicEditorFactory
import os

basedir = os.path.dirname(os.path.realpath(__file__))


class NavigationToolbar(NavigationToolbar2WxAgg): 
    ON_CONFIG  = wx.NewId()

    def __init__(self, canvas, tools=('Home', 'Pan', 'Zoom', 'Save')):
        NavigationToolbar2WxAgg.__init__(self, canvas)
        i = 0
        for pos, tool in enumerate(self.toolitems):
            if tool[0] not in tools:
                self.DeleteToolByPos(pos-i)
                i+=1
        self.AddSimpleTool(self.ON_CONFIG, wx.Bitmap(basedir+'/images/preferences-system-mpl.png'),
                           'Customize', 'Customize')
        wx.EVT_TOOL(self, self.ON_CONFIG, self._on_config)

    def _on_config(self, evt):
        try:
            self.canvas.figure.traited.configure()
        except:
            pass


class _MPLFigureEditor(Editor):
    scrollable  = True

    def init(self, parent):
        self.control = self._create_canvas(parent)
        self.set_tooltip()

    def update_editor(self):
        pass

    def _create_canvas(self, parent):
        """ Create the MPL canvas. """
        # The panel lets us add additional controls.
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        # matplotlib commands to create a canvas
        mpl_control = FigureCanvas(panel, -1, self.value)
        sizer.Add(mpl_control, 1, wx.LEFT | wx.TOP | wx.GROW)
        toolbar = NavigationToolbar(mpl_control)
        toolbar.Realize()
        sizer.Add(toolbar, 0, wx.EXPAND)
        self.value.canvas.SetMinSize((10,10))
        return panel


class MPLFigureEditor(BasicEditorFactory):
    klass = _MPLFigureEditor


if __name__ == "__main__":
    # Create a window to demo the editor
    from matplotlib.figure import Figure
    from traits.api import *
    from traitsui.api import *
    from numpy import sin, cos, linspace, pi
    from matplotlib.widgets import  RectangleSelector


    class MPLInitHandler(Handler):
        """Handler calls mpl_setup() to initialize mpl events"""
        
        def init(self, info):
            """This method gets called after the controls have all been
            created but before they are displayed.
            """
            info.object.mpl_setup()
            return True

    class Test(HasTraits):

        figure = Instance(Figure, ())

        view = View(Item('figure', editor=MPLFigureEditor(),
                         show_label=False),
                    handler=MPLInitHandler,
                    resizable=True,
                    )

        def __init__(self):
            super(Test, self).__init__()
            #self.figure.canvas.SetMinSize((100,100))
            self.axes = self.figure.add_subplot(111)
            t = linspace(0, 2*pi, 200)
            self.axes.plot(sin(t)*(1+0.5*cos(11*t)), cos(t)*(1+0.5*cos(11*t)))

        def mpl_setup(self):
            def onselect(eclick, erelease):
                print "eclick: {}, erelease: {}".format(eclick,erelease)

            self.rs = RectangleSelector(self.axes, onselect,
                                        drawtype='box',useblit=True)

    t = Test()
    t.configure_traits()
