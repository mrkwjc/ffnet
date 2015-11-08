from traits.api import *
from traitsui.api import *
from traits.etsconfig.api import ETSConfig
from matplotlib.figure import Figure
from matplotlib.widgets import  RectangleSelector


if ETSConfig.toolkit == 'wx':
    from mplwx import MPLFigureEditor
if ETSConfig.toolkit == 'qt4':
    from mplqt import MPLFigureEditor


class MPLInitHandler(Handler):
    """Handler calls mpl_setup() to initialize mpl events"""
    
    def init(self, info):
        """This method gets called after the controls have all been
        created but before they are displayed.
        """
        info.object.mpl_setup()
        return True


class MPLFigureSimple(HasTraits):
    figure = Instance(Figure, ())

    def __init__(self):
        super(MPLFigureSimple, self).__init__()
        self.axes = self.figure.add_subplot(111)

    def mpl_setup(self):
        def onselect(eclick, erelease):
            pass

        self.rs = RectangleSelector(self.axes, onselect,
                                    drawtype='box',useblit=True)

    view = View(Item('figure', editor=MPLFigureEditor(),
                     show_label=False),
                     handler=MPLInitHandler,
                     resizable=True,
                     )