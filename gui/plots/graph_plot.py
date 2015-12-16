#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'
from traits.api import *
from traitsui.api import *
import pyface.api as pyface
from mplfigure import MPLPlotter
from graph_layout import layered_layout
# from mpltools import hexcolor
import numpy as np
import networkx as nx
import matplotlib


class GraphPlotter(MPLPlotter):
    graph = Instance(nx.Graph, live = True)
    show_biases = Bool(False, live = True)
    node_labels = Bool(True, live = True)
    node_size = Range(1, 20, 5, live = True)
    edge_width = Range(0.1, 2., 1., live = True)
    layout = Enum('layered', 'spring', 'circular', 'random', live = True)
    #node_color = Color('red', live = True)
    #edge_color = Color('black', live = True)

    def setup(self):
        self.figure.figure.set_facecolor('white')
        self.figure.axes.xaxis.set_visible(False)
        self.figure.axes.yaxis.set_visible(False)
        self.figure.axes.set_frame_on(False)
        self.figure.axes.set_position([0, 0, 1, 1])

    def plot(self, data=None):
        graph = self.__get_graph()
        if graph is None:
            return
        pos = self.__get_pos(graph)
        #if pos is None:
            #return
        matplotlib.rcParams['interactive'] = False
        nx.draw_networkx(graph,
                         pos         = pos,
                         ax          = self.figure.axes,
                         with_labels = self.node_labels,
                         node_color  = '#A0CBE2',  # hexcolor(self.node_color),
                         node_size   = self.node_size*100,
                         edge_color  = 'black',  # hexcolor(self.edge_color),
                         width       = self.edge_width
                         )
        matplotlib.rcParams['interactive'] = True

    def __get_graph(self):
        graph = self.graph
        if graph is not None:
            if 0 in graph.nodes() and not self.show_biases:
                nlist = sorted(graph.nodes())
                graph = graph.subgraph(nlist[1:])
        return graph

    def __get_pos(self, graph):
        if self.layout == 'layered':  # only DAGs
            try:
                pos = layered_layout(graph)
            except:
                import sys
                e = sys.exc_info()[1]
                pyface.error(None, "Layered layout cannot be created!\n\n" + e.message)
                pos  = None
        elif self.layout == 'spring':
            pos = nx.spring_layout(graph)
        elif self.layout == 'circular':
            pos = nx.circular_layout(graph)
        elif self.layout == 'random':
            pos = nx.random_layout(graph)
        else:
            pos = None
        return pos


    traits_view = View(Item('show_biases'),
                Item('node_labels'),
                Item('node_size'),
                Item('edge_width'),
                Item('layout'),
                # Item('node_color', style = 'custom'),
                # Item('edge_color', style = 'custom'),
                resizable = True)


if __name__ == "__main__":
    p = GraphPlotter()
    def randdag():
        G = nx.gnp_random_graph(20,0.5,directed=True)
        DAG = nx.DiGraph([(u,v) for (u,v) in G.edges() if u<v])
        return DAG
    p.graph = randdag()
    p.figure.configure_traits()