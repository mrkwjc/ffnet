from enthought.traits.api import *
from enthought.traits.ui.api import *
from mplfigure import MPLFigureWithControl, FigureControl
from pyface.api import GUI


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
        #self.figure.tight_layout()
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
        ax.set_ylabel('$\sum_i\sum_j\left(o_{ij} - t_{ij}\\right)^2$')
        ax.legend()

    def plot(self, it, err):
        ax = self.axes
        ax.plot(it, err, 'ro-', lw=2, label='Training error')
        ax.legend()
        #self.figure.tight_layout()
        self.draw()
    plott = plot
    
    def plotv(self, it, err):
        ax = self.axes
        ax.plot(it, err, 'gv-', lw=2, label='Validation error')
        ax.legend()
        self.draw()


class Plots(HasTraits):
    selected = Enum('none',
                    'architecture',
                    'error',
                    'out-vs-inp',
                    'out-vs-inp-deriv'
                    'out-vs-trg',
                    'regression')
    architecture = Instance(PreviewFigure, ())
    error = Instance(ErrorFigure, ())

    view = View(UItem('selected'),
                UItem('architecture',
                      visible_when = 'selected == "architecture"',
                      style = 'custom',
                      resizable = True),
                UItem('error',
                      visible_when = 'selected == "error"',
                      style = 'custom',
                      resizable = True),
                resizable = True)
    
    #plot = Enum('Architecture',
                #'Training error',
                #'Output vs. input',
                #'Output vs. input (derivatives)',
                #'Output vs.target',
                #'Regression',
                #'None')

