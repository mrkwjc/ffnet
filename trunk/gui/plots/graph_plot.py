#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'
from traits.api import *
from traitsui.api import *
from mplfigure import MPLPlotter
# from mpltools import hexcolor
import numpy as np
import networkx as nx
import matplotlib


class GraphPlot(MPLPlotter):
    graph = Instance(nx.Graph) #, live = True)
    show_biases = Bool(False) #, live = True)
    node_labels = Bool(True) #, live = True)
    node_size = Range(1, 20, 5) #, live = True)
    edge_width = Range(0.1, 2., 1.) #, live = True)
    layout = Enum('dot') #, live = True)
    draw_network = Button
    #node_color = Color('red', live = True)
    #edge_color = Color('black', live = True)

    def setup(self):
        self.figure.figure.set_facecolor('white')
        self.figure.axes.xaxis.set_visible(False)
        self.figure.axes.yaxis.set_visible(False)
        self.figure.axes.set_frame_on(False)
        self.figure.axes.set_position([0, 0, 1, 1])

    def plot(self):
        graph = self._get_graph()
        if graph is None:
            return
        matplotlib.rcParams['interactive'] = False
        nx.draw_graphviz(graph,
                         ax          = self.figure.axes,
                         prog        = self.layout,
                         with_labels = self.node_labels,
                         node_color  = '#A0CBE2',  # hexcolor(self.node_color),
                         node_size   = self.node_size*100,
                         edge_color  = 'black',  # hexcolor(self.edge_color),
                         width       = self.edge_width
                         )
        matplotlib.rcParams['interactive'] = True

    def _get_graph(self):
        graph = self.graph
        if graph is not None:
            if 0 in graph.nodes() and not self.show_biases:
                nlist = sorted(graph.nodes())
                graph = graph.subgraph(nlist[1:])
        return graph

    def _draw_network_fired(self):
        self._plot()

    view = View(Item('show_biases'),
                Item('node_labels'),
                Item('node_size'),
                Item('edge_width'),
                Item('layout'),
                # Item('node_color', style = 'custom'),
                # Item('edge_color', style = 'custom'),
                UItem('draw_network'),
                resizable = True)

if __name__ == "__main__":
    p = GraphPlot()
    p.graph = nx.balanced_tree(2, 3).to_directed()
    p.figure.configure_traits()