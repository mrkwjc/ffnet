#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *
import numpy as np
import networkx as nx
import matplotlib

from plots.mplfigure import MPLAnimator
from messages import display_error
from graph_layout import layered_layout

class ErrorAnimation(MPLAnimator):
    name = Str('Training error')
    relative_error = Bool(False, live=True)

    def plot_init(self):
        self.figure.axes.clear()
        ax = self.figure.axes
        self.tline, = ax.plot([], [], 'ro-', lw=2, label='Training error')
        self.vline, = ax.plot([], [], 'gv-', lw=2, label='Validation error')
        ax.set_yscale("log")
        ax.grid(True)
        ax.set_xlabel('Iteration')
        #ax.set_ylabel('$\sum_i\sum_j\left(o_{ij} - t_{ij}\\right)^2$')
        ax.set_ylabel('Error')
        ax.legend(loc='best')
        return self.tline, self.vline

    def plot_data(self):
        it = self.app.shared.ilist
        terr = self.app.shared.tlist
        verr = self.app.shared.vlist
        if self.relative_error:
            terr = [t/terr[0] for t in terr]
            verr = [v/verr[0] for v in verr]
        if len(verr) > 0:
            n = min(len(it), len(terr), len(verr))  # instead of synchronization
        else:
            n = min(len(it), len(terr))
        return it[:n], terr[:n], verr[:n]

    def plot(self, data=None):
        it, terr, verr = data #if data is not None else self.plot_data()
        ax = self.figure.axes
        self.tline.set_data(it, terr)
        if len(verr) > 0:
            self.vline.set_data(it, verr)
        self.relim()
        return self.tline, self.vline

    traits_view = View(Item('relative_error'),
                       resizable = True)


class IOAnimation(MPLAnimator):
    name = Str('Input vs. Output')
    app = Any
    inputs = Property(List, depends_on='app.network.net', transient=True)
    outputs = Property(List, depends_on='app.network.net', transient=True)
    i = Enum(values='inputs', live=True, transient=True)
    o = Enum(values='outputs', live=True, transient=True)

    def _get_inputs(self):
        if self.app is not None and self.app.network.net is not None:
            return range(1, len(self.app.network.net.inno)+1)
        return []

    def _get_outputs(self):
        if self.app is not None and self.app.network.net is not None:
            return range(1, len(self.app.network.net.outno)+1)
        return []

    def plot_init(self):
        self.figure.axes.clear()
        ax = self.figure.axes
        self.oline, = ax.plot([], [], 'ko-', ms=7, mfc='w', mew=1.2, lw=1.2, label='Input - Output')
        self.tline, = ax.plot([], [], 'ro--', ms=4, lw=1, label='Input - Training Target')
        self.vline, = ax.plot([], [], 'gv', ms=4, label='Input - Validation Target')
        ax.grid(True)
        ax.set_xlabel('Input %i' %self.i)
        ax.set_ylabel('Output %i' %self.o)
        ax.legend(loc='best')
        self.setlim()
        return self.oline, self.tline, self.vline

    def plot_data(self):
        if self.app.network.net is None or self.app.data.status != 2:
            return
        inp = self.app.data.input[:, self.i-1]
        out = self.app.network.net(self.app.data.input)[:, self.o-1]
        trg = self.app.data.target[:, self.o-1]
        vmask = self.app.data.vmask
        argsort = inp.argsort()
        return inp[argsort], out[argsort], trg[argsort], vmask[argsort]

    def animation_data(self):
        while self.running:
            self.app.network.net.weights[:] = self.app.shared.wlist[-1]
            yield self.plot_data()

    def plot(self, data=None):
        if data is None:
            return
        inp, out, trg, vmask = data
        self.oline.set_data(inp, out)
        self.tline.set_data(inp, trg)
        self.vline.set_data(inp[vmask], trg[vmask])
        return self.oline, self.tline, self.vline

    def setlim(self):
        ax = self.figure.axes
        if self.app.data.status > 0:
            inp = self.app.data.input[:, self.i-1]
            xl = min(inp) - (max(inp)-min(inp))*0.1
            xr = max(inp) + (max(inp)-min(inp))*0.1
            ax.set_xlim(xl, xr)
        if self.app.data.status > 1:
            trg = self.app.data.target[:, self.o-1]
            yl = min(trg) - (max(trg)-min(trg))*0.1
            yr = max(trg) + (max(trg)-min(trg))*0.1
            ax.set_ylim(yl, yr)

    traits_view = View(Item('i', label='Input'),
                       Item('o', label='Output'),
                       resizable = True)


class TOAnimation(MPLAnimator):
    name = Str('Target vs. Output')
    app = Any  # nedede by below Property
    outputs = Property(List, depends_on='app.network.net', transient=True)
    output = Enum(values='outputs', live=True, transient=True)

    def _get_outputs(self):
        if self.app is not None and self.app.network.net is not None:
            return range(len(self.app.network.net.outno))
        return []

    def plot_init(self):
        self.figure.axes.clear()
        ax = self.figure.axes
        self.tline, = ax.plot([], [], 'ro', label='Training data')
        self.vline, = ax.plot([], [], 'gv', label='Validation data')
        self.rline, = ax.plot([], [], 'k', lw=1.2, label='Regression line')
        ax.grid(True)
        ax.set_xlabel('Targets')
        ax.set_ylabel('Outputs')
        ax.legend(loc='best')
        return self.tline, self.vline, self.rline

    def plot_data(self):
        if self.app.network.net is None or self.app.data.status != 2:
            return
        i = self.app.data.input
        t = self.app.data.target
        vmask = self.app.data.vmask
        o, r = self.app.network.net.test(i, t, iprint = 0)
        slope = r[0][0]
        intercept = r[0][1]
        offset = (t.max() - t.min())*0.05
        x = np.linspace(t.min()-offset, t.max()+offset)
        y = slope * x + intercept
        tt = t[~vmask][:, self.output]
        tv = t[vmask][:, self.output]
        ot = o[~vmask][:, self.output]
        ov = o[vmask][:, self.output]
        return tt, ot, tv, ov, x, y

    def animation_data(self):
        while self.running:
            self.app.network.net.weights[:] = self.app.shared.wlist[-1]
            yield self.plot_data()

    def plot(self, data=None):
        if data is None:
            return
        tt, ot, tv, ov, x, y = data #if data is not None else self.plot_data()
        ax = self.figure.axes
        self.tline.set_data(tt, ot)
        self.vline.set_data(tv, ov)
        self.rline.set_data(x, y)
        self.relim()
        return self.tline, self.vline, self.rline

    traits_view = View(Item('output', label = 'Network output'),
                            resizable = True)


class GraphAnimation(MPLAnimator):
    name = "Network architecture"
    graph = Instance(nx.Graph)
    graph_no_biases = Instance(nx.Graph)
    pos = Dict
    pos_no_biases = Dict
    show_biases = Bool(False, live = True)
    node_labels = Bool(True, live = True)
    node_size = Range(1, 20, 5, live = True)
    edge_width = Range(0.1, 2., 1., live = True)
    layout = Enum('layered', 'spring', 'circular', 'random', live = True)
    colorize_edges = Bool(False, live = True)
    colorize_nodes = Bool(False, live = True)
    input_pattern = Int(1, live = True)
    app = Any  # necessary for below property...
    ninp = Property(Int(1), depends_on='app.data.input')

    def setup(self):
        self.figure.figure.set_facecolor('white')
        self.figure.axes.xaxis.set_visible(False)
        self.figure.axes.yaxis.set_visible(False)
        self.figure.axes.set_frame_on(False)
        self.figure.axes.set_position([0, 0, 1, 1])

    def plot_data(self):
        if self.graph is None:
            return
        # Get some input and units values
        inp = [0.]*len(self.app.network.net.inno)
        if self.app.data.status > 0:
            if self.app.data.input.shape[1] == len(self.app.network.net.inno): # test in data?
                inp = self.app.data.input[self.input_pattern-1]
        self.app.network.net(inp)
        units = self.app.network.net.units.tolist()
        # Get colors numbers
        if self.show_biases and 0 in self.graph:
            node_color = [1.] + units
            nodelist = range(0, len(units)+1)
            edge_color = self.app.network.net.weights
            edgelist = self.app.network.net.conec.tolist()
        else:
            node_color = units
            nodelist = range(1, len(units)+1)
            emask = self.app.network.net.conec.T[0] != 0
            edge_color = self.app.network.net.weights[emask]
            edgelist = self.app.network.net.conec[emask].tolist()
        if not self.colorize_nodes:
            node_color = [0. for n in node_color]
        if not self.colorize_edges:
            edge_color = [1. for n in edge_color]
        return nodelist, node_color, edgelist, edge_color

    def animation_data(self):
        self.colorize_edges = True  # To see something
        self.colorize_nodes = True  # To see something
        while self.running:
            self.figure.axes.clear()  # Always clear before next step (we do not update in plot!)
            self.app.network.net.weights[:] = self.app.shared.wlist[-1]
            yield self.plot_data()

    def plot(self, data=None):
        if data is None:
            return
        nodelist, node_color, edgelist, edge_color = data
        if self.show_biases:
            graph = self.graph 
            pos = self.pos
        else:
            graph = self.graph_no_biases
            pos = self.pos_no_biases
        matplotlib.rcParams['interactive'] = False
        nx.draw_networkx(graph.to_undirected(),
                         pos         = pos,
                         ax          = self.figure.axes,
                         nodelist    = nodelist,
                         edgelist    = edgelist,
                         with_labels = self.node_labels,
                         node_size   = self.node_size*100,
                         node_color  = node_color,
                         cmap        = matplotlib.cm.Blues,
                         vmin        = 0.,
                         vmax        = 1.,
                         edge_color  = edge_color,
                         edge_cmap   = matplotlib.cm.Blues,
                         edge_vmin   = -1.,
                         edge_vmax   = 1.,
                         width       = self.edge_width
                         )
        matplotlib.rcParams['interactive'] = True

    def _calculate_pos(self, graph):
        if self.layout == 'layered':  # only DAGs
            try:
                pos = layered_layout(graph)
            except:
                display_error("Layered layout cannot be created!")
                pos  = None
        elif self.layout == 'spring':
            pos = nx.spring_layout(graph)
        elif self.layout == 'circular':
            pos = nx.circular_layout(graph)
        elif self.layout == 'random':
            pos = nx.random_layout(graph)
        else:
            pos = None  # which gives 'spring' layout...
        return pos

    def _layout_changed(self):
        self.pos = self._calculate_pos(self.graph)
        self.pos_no_biases = self._calculate_pos(self.graph_no_biases)
        self.replot()

    @on_trait_change('app.network.net')
    def _assign_graph(self):
        if self.app is not None and self.app.network.net is not None:
            graph = self.app.network.net.graph.copy()
            self.graph = graph
            if 0 in graph:
                graph = graph.copy()
                graph.remove_node(0)
            self.graph_no_biases = graph
            self._layout_changed()
        else:
            self.graph = None
            self.graph_no_biases = None
            self.pos = {}
            self.pos_no_biases = {}
            self.replot()

    def _get_ninp(self):
        if self.app is not None and self.app.data.status > 0:
            return max(1, len(self.app.data.input))
        else:
            return 0

    traits_view = View(Item('show_biases'),
                Item('node_labels'),
                Item('node_size'),
                Item('edge_width'),
                Item('layout'),
                Item('colorize_edges'),
                Item('colorize_nodes'),
                Item('input_pattern', visible_when='colorize_nodes and ninp',
                     editor = RangeEditor(low=0, high_name='ninp')),
                resizable = True)


if __name__ == "__main__":
    p = IOAnimation(app = None)
    p.configure_traits(view='figure_view')
