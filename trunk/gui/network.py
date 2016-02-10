#-*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

## from traits.etsconfig.api import ETSConfig
## ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *
import pyface.api as pyface
import os

from ffnet import *
from messages import display_error
from animations import GraphAnimation


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
            display_error("Network cannot be created!")
            self.net = None
            return None

    def _preview_button_fired(self):
        net = self.create()
        if net is not None:
            from ffnetapp import FFnetApp
            app = FFnetApp()  # copy.deepcopy(self.app)  # Use copy
            app.net = net
            fig = GraphAnimation(app = app)
            fig.configure_traits(kind='livemodal', view='figure_view')

    traits_view = View(Item('architecture', has_focus=True, tooltip='Layered architecture string, e.g: 3-10-5-1'),
                       Item('connectivity_type'),
                       Item('biases'),
                       UItem('preview_button', label = 'Preview'),
                       handler = CreateHandler(),
                       buttons = [OKButton, CancelButton],
                       resizable=True,
                       title = 'Layered network creation',
                       width=0.2)


class Network(HasTraits):
    net = Any
    filename = Str

    def create(self):
        creator = NetworkCreator(app=self.app)
        creator.edit_traits(kind='livemodal')
        net = creator.net
        if net:
            self.close()  # close old network
            self.net = net
            self.filename = net.name
            self.app.logs.logger.info('Network created: %s' %self.filename)
            return net

    def load(self):
        wildcard = 'Network file (*.net)|*.net|Any file (*.*)|*.*'
        dialog = pyface.FileDialog(parent=None,
                                   title='Load network',
                                   action='open',
                                   wildcard=wildcard,
                                   )
        if dialog.open() == pyface.OK:
            path = dialog.path
            if not os.path.isfile(path):
                display_error("File '%s' does not exist."%path)
                return
            try:
                net = loadnet(path)
                net.weights  # is this network?
                self.close()  # close old network
                self.net = net
                self.filename = path
                self.app.logs.logger.info('Network loaded: %s' %self.filename)
                return net
            except:
                display_error("Wrong network file.")
                return

    def save_as(self):
        if self.net is None:
           display_error("Network neither created nor loaded!")
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
            self.app.logs.logger.info('Network saved as: %s' %self.filename)

    def export(self):
        if self.net is None:
           display_error("Network neither created nor loaded!")
           return
        wildcard = 'Fortran file (*.f)|*.f|Any file (*.*)|*.*'
        outfile = os.path.splitext(self.filename)[0] + '.f'
        dialog = pyface.FileDialog(parent=None,
                                   title='Export as',
                                   action='save as',
                                   wildcard=wildcard,
                                   default_path=outfile
                                   )
        if dialog.open() == pyface.OK:  # path is given
            path = dialog.path
            if not os.path.basename(path).endswith('.f'):
                path += '.f'
            exportnet(self.net, path)
            self.app.logs.logger.info('Network exported as: %s' %path)

    def close(self):
        if self.net:
            # self.app.clear()
            self.app.logs.logger.info('Network closed: %s' %self.filename)
            self.net = None
            self.filename = ''

# Do tests
if __name__ == "__main__":
    n = NetworkCreator()
    n.configure_traits()