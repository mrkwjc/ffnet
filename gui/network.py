from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.traits.ui.file_dialog import open_file, save_file
from enthought.traits.ui.ui_editors.array_view_editor import ArrayViewEditor
import pyface.api as pyface

from ffnet_import import *

from plots.graph_plot import GraphPlotter
import matplotlib
import networkx as nx
import os

#from logger import HasLogger

class CreateHandler(Handler):
    def close(self, info, is_ok):
        if is_ok:
            net = info.object.create()
            return net
        else:
            info.object.net = None
            return True

class NetworkCreator(HasTraits):
    architecture = Str
    connectivity_type = Enum('mlgraph', 'tmlgraph', 'imlgraph')
    biases = Bool(True)
    net = Any
    preview_button = Button
    preview_figure = Instance(GraphPlotter, ())

    def create(self):
        try:
            conn = self.connectivity_type
            arch = self.architecture.replace('-', ',')
            biases = self.biases
            conec = eval('%s((%s), biases=%s)' %(conn, arch, biases))
            self.net = ffnet(conec)
            self.net.name = self.architecture.replace(',', '-')
            return self.net
        except:
            import sys
            e = sys.exc_info()[1]
            pyface.error(None, "Network cannot be created!\n\n" + e.message)
            self.net = None
            return None

    def _preview_button_fired(self):
        net = self.create()
        if net:
            self.preview_figure.graph = net.graph
            self.preview_figure.figure.configure_traits(kind='livemodal')

    traits_view = View(Item('architecture', has_focus=True),
                       Item('connectivity_type'),
                       Item('biases'),
                       #Item('object.preview_figure.biases', label='Biases in preview'),
                       UItem('preview_button', label = 'Preview'),
                       handler = CreateHandler(),
                       buttons = [OKButton, CancelButton],
                       resizable=True,
                       title = 'Layered network creation',
                       width=0.2)

class Network(HasTraits):
    net = Any
    filename = Str
    creator = Instance(NetworkCreator, ())

    def create(self, logger=None):
        #nc = NetworkCreator()
        self.creator.edit_traits(kind='livemodal')
        net = self.creator.net
        if net:
            self.close(logger=logger)
            self.net = net
            self.filename = net.name
            if logger:
                logger.info('Network created: %s' %self.filename)

    def load(self, logger=None):
        wildcard = 'Network file (*.net)|*.net|Any file (*.*)|*.*'
        dialog = pyface.FileDialog(parent=None,
                                   title='Load network',
                                   action='open',
                                   wildcard=wildcard,
                                   )
        if dialog.open() == pyface.OK:
            path = dialog.path
            if not os.path.isfile(path):
                pyface.error(None, "File '%s' does not exist!"%path)
                return
            try:
                net = loadnet(path)
                net.weights  # is this network?
                self.close(logger=logger)
                self.net = net
                self.filename = path
            except:
                pyface.error(None, "Wrong network file.\n")
                return
            if logger:
                logger.info('Network loaded: %s' %self.filename)


    def save_as(self, logger=None):
        if self.net is None:
           pyface.error(None, "Network neither created nor loaded!\n")
           return
        wildcard = 'Network file (*.net)|*.net|Any file (*.*)|*.*'
        dialog = pyface.FileDialog(parent=None,
                                   title='Save as',
                                   action='save as',
                                   wildcard=wildcard,
                                   default_path=self.filename
                                   )
        if dialog.open() == pyface.OK:  # path is given
            path = dialog.path
            if not os.path.basename(path).endswith('.net'):
                path += '.net'
            savenet(self.net, path)
            self.filename = path
            if logger:
                logger.info('Network saved as: %s' %self.filename)
    
    def close(self, logger=None):
        if self.net:
            if logger:
                logger.info('Network closed: %s' %self.filename)
            self.net = None
            self.filename = ''


#class NetworkHandler(Handler):
    ##def create_button_handler(self, info):
        ##if not info.initialized: 
            ##return  # needed if info takes long to initialize
        ##success = info.object.create_network()
        ##self.closed(info, success)
        ##if success:
            ##info.ui.dispose(success) # Close window

    #def close(self, info, is_ok):
        #if is_ok:
            #success = info.object.create_network()
            #return success
        #else:
            #info.object.net = None
            #return True  # Handler.close(self, info, is_ok)


#class Network(HasTraits):
    #name = Str
    #file_name = File
    #architecture = Str #Str('2, 2, 1')
    #connectivity_type = Enum('mlgraph', 'tmlgraph', 'imlgraph')
    #biases = Bool(True)
    #biases_in_preview = Bool(False)
    #net = Any  #Instance(ffnet) #, (mlgraph((2, 2, 1)), True))
    #info = Property
    #preview_button = Button
    #preview_figure = Instance(PreviewFigure, ())

    #def __repr__(self):
        #return self.name

    #def _architecture_changed(self):
        #self.net=None

    #def _connectivity_type_changed(self):
        #self.net=None

    #def _biases_changed(self):
        #self.net=None

    #@property
    #def info(self):
        #if self.net is not None:
            #return '\n' + self.net.__repr__()
        #return '\n'

    #def create_network(self):
        #try:
            #conn = self.connectivity_type
            #arch = self.architecture.replace('-', ',')
            #biases = self.biases
            #conec = eval('%s((%s), biases=%s)' %(conn, arch, biases))
            #self.net = ffnet(conec)
            #self.name = self.architecture.replace(',', '-') + ' [not saved]'
            #return True
        #except:
            #import sys
            #e = sys.exc_info()[1]
            #pyface.error(None, "Network cannot be created!\n\n" + e.message)
            #return False

    #def save_as(self):
        #if self.net is None:
           #pyface.error(None, "Network neither created nor loaded!\n")
           #return
        #wildcard = 'Network file (*.net)|*.net'
        #dialog = pyface.FileDialog(parent=None,
                                   #title='Save as',
                                   #action='save as',
                                   #wildcard=wildcard,
                                   #default_path=self.file_name
                                   #)
        #if dialog.open() == pyface.OK:  # path is given
            #path = dialog.path
            #if not os.path.basename(path).endswith('.net'):
                #path += '.net'
            #savenet(self.net, path)
            #self.file_name = path
            #self.name = os.path.splitext(os.path.basename(path))[0]
            #return True

    #def load(self):
        #wildcard = 'Network file (*.net)|*.net'
        #dialog = pyface.FileDialog(parent=None,
                                   #title='Load network',
                                   #action='open',
                                   #wildcard=wildcard,
                                   ##default_path=self.file_name
                                   #)
        #if dialog.open() == pyface.OK:
            #path = dialog.path
            #if not os.path.isfile(path):
                #pyface.error(None, "File '%s' does not exist!"%path)
                #return False
            #try:
                #self.net = loadnet(path)  #try, except
            #except:
                #import sys
                #pyface.error(None, "Network cannot be loaded!\nWrong network file.\n")
                #return False
            #self.file_name = path
            #self.name = os.path.splitext(os.path.basename(path))[0]
            #return True
        #return False

    #def _preview_button_fired(self):
        #ok = True
        #if self.net is None:
            #ok = self.create_network()
        #if ok:
            #self.preview_figure.show_status = False
            #self.preview_figure.biases_in_preview = self.biases_in_preview
            #self.preview_figure.net = self.net
            #self.preview_figure.show_status = True
            #self.preview_figure.edit_traits(view='simple_view', kind='live')

    #traits_view = View(Item('architecture', has_focus=True),
                       #Item('connectivity_type'),
                       #Item('biases'),
                       #Item('biases_in_preview'),
                       #UItem('preview_button', label = 'Preview'),
                       #handler = NetworkHandler(),
                       #buttons = [OKButton, CancelButton],
                       #resizable=True,
                       #width=0.2)

    #preview_view = View(UItem('preview_figure', style='custom'))


# Do tests
if __name__ == "__main__":
    n = NetworkCreator()
    n.configure_traits()