#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — March 2014
""" traitsui matplotlib editor with toolbar using qt backend 
publicaly shared by Ryan Olf, April 2013

Source:
http://enthought-dev.117412.n3.nabble.com/traitsui-matplotlib-editor-with-toolbar-using-qt-backend-td4026437.html
"""
import matplotlib
import matplotlib as mpl
mpl.rcParams['backend.qt4']='PySide'
mpl.use('Qt4Agg')

from pyface.qt import QtGui, QtCore
from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'


# We want matplotlib to use a QT backend
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
from matplotlib.backends.qt_compat import QtWidgets

from traits.api import Any, Instance
from traitsui.qt4.editor import Editor
from traitsui.qt4.basic_editor_factory import BasicEditorFactory
from traitsui.api import Handler
import os

class NavigationToolbar(NavigationToolbar2QTAgg):
    def __init__(self, canvas, parent, tools=('Home', 'Pan', 'Zoom', 'Save'), **kwargs):
        mpl.backends.backend_qt4.figureoptions = None
        mpl.backends.backend_qt5.figureoptions = None
        self.toolitems = [t for t in NavigationToolbar2QTAgg.toolitems if t[0] in tools]
        NavigationToolbar2QTAgg.__init__(self, canvas, parent, **kwargs)

    def custom_tools(self):
        """
        We define custom actions here
        """
        icon = QtGui.QIcon('images/preferences-system-mpl.png')
        tool = self.addAction(icon, 'Customize', self._on_config)
        tool.setToolTip('Customize')

    def _on_config(self):
        try:
            self.canvas.figure.traited.configure()
        except:
            pass

    # We need to overwite also this for custom tool...
    def _init_toolbar(self):
        self.basedir = os.path.join(matplotlib.rcParams['datapath'], 'images')

        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                self.addSeparator()
            else:
                a = self.addAction(self._icon(image_file + '.png'),
                                         text, getattr(self, callback))
                self._actions[callback] = a
                if callback in ['zoom', 'pan']:
                    a.setCheckable(True)
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)

        #if figureoptions is not None:
            #a = self.addAction(self._icon("qt4_editor_options.png"),
                               #'Customize', self.edit_parameters)
            #a.setToolTip('Edit curves line and axes parameters')

        ### CUSTOM TOOLS
        self.custom_tools()
        ### CUSTOM  TOOLS

        self.buttons = {}

        # Add the x,y location widget at the right side of the toolbar
        # The stretch factor is 1 which means any resizing of the toolbar
        # will resize this label instead of the buttons.
        if self.coordinates:
            self.locLabel = QtWidgets.QLabel("", self)
            self.locLabel.setAlignment(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            self.locLabel.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Ignored))
            labelAction = self.addWidget(self.locLabel)
            labelAction.setVisible(True)

        # reference holder for subplots_adjust window
        self.adj_window = None


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
       mpl_toolbar = NavigationToolbar(mpl_canvas,frame)

       vbox = QtGui.QVBoxLayout()
       vbox.addWidget(mpl_canvas)
       vbox.addWidget(mpl_toolbar)
       frame.setLayout(vbox)

       return frame


class MPLFigureEditor(BasicEditorFactory):
   klass = _MPLFigureEditor


if __name__ == "__main__":
    # Create a window to demo the editor
    from traits.api import HasTraits
    from traitsui.api import View, Item
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
