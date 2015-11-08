from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.traits.ui.file_dialog import open_file, save_file
from enthought.traits.ui.ui_editors.array_view_editor import ArrayViewEditor
import pyface.api as pyface

from ffnet_import import *

from mplfigure import MPLFigureSimple
import matplotlib
import networkx as nx
import os


class NetworkHandler(Handler):
    #def create_button_handler(self, info):
        #if not info.initialized: 
            #return  # needed if info takes long to initialize
        #success = info.object.create_network()
        #self.closed(info, success)
        #if success:
            #info.ui.dispose(success) # Close window

    def close(self, info, is_ok):
        if is_ok:
            success = info.object.create_network()
            return success
        else:
            info.object.net = None
            return True  # Handler.close(self, info, is_ok)


class Network(HasTraits):
    name = Str
    file_name = File
    architecture = Str #Str('2, 2, 1')
    connectivity_type = Enum('mlgraph', 'tmlgraph', 'imlgraph')
    biases = Bool(True)
    biases_in_preview = Bool(False)
    net = Any  #Instance(ffnet) #, (mlgraph((2, 2, 1)), True))
    #create_button = Action(name = 'Create', action = 'create_button_handler')
    preview = Button
    preview_figure = Instance(MPLFigureSimple, ())

    def __repr__(self):
        return self.name

    def create_network(self):
        try:
            conn = self.connectivity_type
            arch = self.architecture.replace('-', ',')
            biases = self.biases
            conec = eval('%s((%s), biases=%s)' %(conn, arch, biases))
            self.net = ffnet(conec)
            self.name = self.architecture.replace(',', '-') + ' [not saved]'
            return True
        except:
            import sys
            e = sys.exc_info()[1]
            pyface.error(None, "Network cannot be created!\n\n" + e.message)
            return False

    def save_as(self):
        wildcard = 'Network file (*.net)|*.net'
        dialog = pyface.FileDialog(parent=None,
                                   title='Save as',
                                   action='save as',
                                   wildcard=wildcard,
                                   default_path=self.file_name
                                   )
        if dialog.open() == pyface.OK:  # path is given
            path = dialog.path
            if not os.path.basename(path).endswith('.net'):
                path += '.net'
            savenet(self.net, path)
            self.file_name = path
            self.name = os.path.splitext(os.path.basename(path))[0]
            return True

    def load(self):
        wildcard = 'Network file (*.net)|*.net'
        dialog = pyface.FileDialog(parent=None,
                                   title='Load network',
                                   action='open',
                                   wildcard=wildcard,
                                   #default_path=self.file_name
                                   )
        if dialog.open() == pyface.OK:
            path = dialog.path
            if not os.path.isfile(path):
                pyface.error(None, "File '%s' does not exist!"%path)
                return
            self.net = loadnet(path)
            self.file_name = path
            self.name = os.path.splitext(os.path.basename(path))[0]
            return True

    def _preview_fired(self):
        success = self.create_network()
        if success:
            graph = self.net.graph
            nlist = sorted(self.net.graph.nodes())
            if not self.biases_in_preview:
                graph = graph.subgraph(nlist[1:])
            axes = self.preview_figure.axes
            matplotlib.rcParams['interactive']=False
            nx.draw_graphviz(graph, ax = axes, prog='dot', with_labels=True,
                            node_color='#A0CBE2', node_size=500,
                            edge_color='k')
            matplotlib.rcParams['interactive']=True
            self.preview_figure.edit_traits(kind='livemodal')
            #self.edit_traits(view='preview_view', kind='livemodal')

    traits_view = View(Item('architecture', has_focus=True),
                       Item('connectivity_type'),
                       Item('biases'),
                       Item('biases_in_preview'),
                       UItem('preview'),
                       handler = NetworkHandler(),
                       buttons = [OKButton, CancelButton],
                       resizable=True,
                       width=0.2)
    
    #preview_view = View(UItem('preview_figure', style='custom'))


# Do tests
if __name__ == "__main__":
    n = Network()
    n.configure_traits()