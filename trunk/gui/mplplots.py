from enthought.traits.api import *
from enthought.traits.ui.api import *
from mplfigure import MPLFigureWithControl, FigureControl
from pyface.api import GUI

class Plots(HasTraits):
    plot = Enum('Architecture',
                'Training error',
                'Output vs. input',
                'Output vs. input (derivatives)',
                'Output vs.target',
                'Regression',
                'None')
    #arch = Instance(PreviewFigure, ())
    #error = Instance(ErrorFigure, ())


class PreviewFigureControl(FigureControl):
    net = Any
    show_bias_node = Bool(False)

    def _net_changed(self):
        self.figure.reset()
        self.figure.plot()

    def _show_bias_node_changed(self):
        self.figure.reset()
        self.figure.plot()

    view = View(Item('show_bias_node'))


class PreviewFigure(MPLFigureWithControl):
    control = Instance(PreviewFigureControl, ())
    # net = DelegatesTo('control')
    # show_bias_node = DelegatesTo('control')

    def setup(self):
        self.figure.set_facecolor('white')
        self.axes.xaxis.set_visible(False)
        self.axes.yaxis.set_visible(False)
        self.axes.set_frame_on(False)

    def plot(self):
        net = self.control.net
        show_bias_node = self.control.show_bias_node
        if net is None:
            return
        import matplotlib
        import networkx as nx
        graph = net.graph
        if 0 in net.graph.nodes() and not show_bias_node:
            nlist = sorted(net.graph.nodes())
            graph = graph.subgraph(nlist[1:])
        axes = self.axes
        matplotlib.rcParams['interactive']=False
        nx.draw_graphviz(graph, ax = axes, prog='dot', with_labels=True,
                            node_color='#A0CBE2', node_size=500,
                            edge_color='k')
        matplotlib.rcParams['interactive']=True
        self.figure.tight_layout()
        self.draw()


class ErrorFigureControl(FigureControl):
    grid = Bool(True)

    def _grid_changed(self):
        self.figure.axes.grid(self.grid)
        self.figure.draw()

    view = View(Item('grid'))


class ErrorFigure(MPLFigureWithControl):
    control = Instance(ErrorFigureControl, ())

    def setup(self):
        ax = self.axes
        ax.set_yscale("log")
        ax.grid(self.control.grid)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('$$\sum_i\sum_j\left(o_{ij} - t_{ij}\\right)^2$$')
        #ax.set_title('Training error')
        self.figure.tight_layout()
        ax.legend()

    def plot(self, it, err):
        ax = self.axes
        ax.plot(it, err, 'ro-', lw=2, label='Training error')
        ax.legend()
        self.draw()
    plott = plot
    
    def plotv(self, it, err):
        ax = self.axes
        ax.plot(it, err, 'gv-', lw=2, label='Validation error')
        ax.legend()
        self.draw()

#class PreviewFigure(MPLFigureSimple):
    #show = Button
    #show_status = Bool(False)
    #net = Any
    #biases_in_preview = Bool(False)
    #self._plotted = Bool(False)

    #def __init__(self, net=None, biases_in_preview=False):
        #super(PreviewFigure, self).__init__()
        #self.net = net
        #self.biases_in_preview = biases_in_preview

    #def _show_fired(self):
        #self.show_status = not self.show_status

    #def _show_status_changed(self):
        #if self.show_status:
            #self.plot()
    
    #def _net_changed(self):
        #self._plotted = False
        #if self.show_status:
            #self.plot()

    #def _biases_in_preview_changed(self):
        #self._plotted = True
        #if self.show_status:
            #self.plot()

    #def mpl_setup(self):
        #self.figure.set_facecolor('white')
        #self.axes.xaxis.set_visible(False)
        #self.axes.yaxis.set_visible(False)
        #self.axes.set_frame_on(False)
        ##self.axes.axis('off')

    #def plot(self):
        #if self.net is None or self._plotted:
            #return
        #import matplotlib
        #import networkx as nx
        #self.axes.clear()
        #net = self.net
        #graph = net.graph
        #if 0 in net.graph.nodes() and not self.biases_in_preview:
            #nlist = sorted(net.graph.nodes())
            ## if not self.biases_in_preview:
            #graph = graph.subgraph(nlist[1:])
        #axes = self.axes
        #matplotlib.rcParams['interactive']=False
        #nx.draw_graphviz(graph, ax = axes, prog='dot', with_labels=True,
                            #node_color='#A0CBE2', node_size=500,
                            #edge_color='k')
        #matplotlib.rcParams['interactive']=True
        #self.figure.tight_layout()
        #self._plotted = True

    #traits_view = View(UItem('show'),
                       #UItem('figure', editor=MPLFigureEditor(), visible_when='show_status'),
                       #handler=MPLInitHandler,
                       #resizable=True,
                       #)
