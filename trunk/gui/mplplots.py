from enthought.traits.api import *
from enthought.traits.ui.api import *
from mplfigure import MPLFigureSimple, MPLInitHandler, MPLFigureEditor

class PreviewFigure(MPLFigureSimple):
    net = Any
    biases = Bool(False)

    def mpl_setup(self):
        self.figure.set_facecolor('white')
        self.axes.xaxis.set_visible(False)
        self.axes.yaxis.set_visible(False)
        self.axes.set_frame_on(False)

    def _net_changed(self):
        self.plot()

    def _biases_changed(self):
        self.plot()

    def plot(self):
        if self.net is None:
            return
        import matplotlib
        import networkx as nx
        self.axes.clear()
        net = self.net
        graph = net.graph
        if 0 in net.graph.nodes() and not self.biases:
            nlist = sorted(net.graph.nodes())
            graph = graph.subgraph(nlist[1:])
        axes = self.axes
        matplotlib.rcParams['interactive']=False
        nx.draw_graphviz(graph, ax = axes, prog='dot', with_labels=True,
                            node_color='#A0CBE2', node_size=500,
                            edge_color='k')
        matplotlib.rcParams['interactive']=True
        self.figure.tight_layout()

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
