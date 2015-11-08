#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — March 2014
""" traitsui matplotlib editor with toolbar using qt backend 
publicaly shared by Ryan Olf, April 2013

Source:
http://enthought-dev.117412.n3.nabble.com/traitsui-matplotlib-editor-with-toolbar-using-qt-backend-td4026437.html
"""

from pyface.qt import QtGui, QtCore
from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'

import matplotlib as mpl
mpl.rcParams['backend.qt4']='PySide'

# We want matplotlib to use a QT backend
mpl.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg

from traits.api import Any, Instance
from traitsui.qt4.editor import Editor
from traitsui.qt4.basic_editor_factory import BasicEditorFactory
from traitsui.api import Handler

class _MPLFigureEditor(Editor):

   scrollable  = True

   def init(self, parent):
       self.control = self._create_canvas(parent)
       self.set_tooltip()

   def update_editor(self):
       pass

   def _create_canvas(self, parent):
       """ Create the MPL canvas. """
       # matplotlib commands to create a canvas
       frame = QtGui.QWidget()
       mpl_canvas = FigureCanvas(self.value)
       mpl_canvas.setParent(frame)
       mpl_toolbar = NavigationToolbar2QTAgg(mpl_canvas,frame)

       vbox = QtGui.QVBoxLayout()
       vbox.addWidget(mpl_canvas)
       vbox.addWidget(mpl_toolbar)
       frame.setLayout(vbox)

       return frame

class MPLFigureEditor(BasicEditorFactory):

   klass = _MPLFigureEditor

class MPLInitHandler(Handler):
    """Handler calls mpl_setup() to initialize mpl events"""
    
    def init(self, info):
        """This method gets called after the controls have all been
        created but before they are displayed.
        """
        info.object.mpl_setup()
        return True

if __name__ == "__main__":
    # Create a window to demo the editor
    from traits.api import HasTraits
    from traitsui.api import View, Item
    from numpy import sin, cos, linspace, pi
    from matplotlib.widgets import  RectangleSelector

    class Test(HasTraits):

        figure = Instance(Figure, ())

        view = View(Item('figure', editor=MPLFigureEditor(),
                         show_label=False),
                    handler=MPLInitHandler,
                    resizable=True)

        def __init__(self):
            super(Test, self).__init__()
            self.axes = self.figure.add_subplot(111)
            t = linspace(0, 2*pi, 200)
            self.axes.plot(sin(t)*(1+0.5*cos(11*t)), cos(t)*(1+0.5*cos(11*t)))

        def mpl_setup(self):
            def onselect(eclick, erelease):
                print "eclick: {}, erelease: {}".format(eclick,erelease)
               
            self.rs = RectangleSelector(self.axes, onselect,
                                        drawtype='box',useblit=True)

    Test().configure_traits()
