#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from enthought.traits.api import *
from enthought.traits.ui.api import *
from pyface.api import GUI
from loadtxt import LoadTxt
from network import Network
from training import TncTrainer
import thread
import sys
import time
import uuid

from mplfigure import MPLFigureEditor
from logger import Logger
from bars import toolbar, menubar

class Trainer(HasTraits):
    netlist = List(values=Instance(Network))
    network = Enum(values='netlist')
    new = Button
    remove = Button
    save_as = Button
    load = Button
    export = Button
    #
    input_data = Instance(LoadTxt, ())
    target_data = Instance(LoadTxt, ())
    trainers = List([TncTrainer()])
    train_algorithm = Enum(values='trainers')
    logs = Instance(Logger, ())

    _garbage = Str
    values=Dict  # Put here variables to be accesible via shell

    def __init__(self, **traits):
        HasTraits.__init__(self, **traits)
        self.logger = self.logs.logger

    def _new(self):
        n = Network()
        n.edit_traits(kind='livemodal')
        if n.net is not None:
            self.netlist.append(n)
            self.network = n
            self.logger.info('Network created: %s' %n.name)

    def _remove(self):
        if len(self.netlist) != 0:
            idx = self.netlist.index(self.network)
            name = self.network.name
            del self.netlist[idx]
            self.logger.info('Network removed: %s' %name)

    def _save_as(self):
        oldname = self.network.name
        success = self.network.save_as() # Open dialog
        if success:
            # Hack for changing name in the Enum list
            n = self.network
            self.netlist.append(Network())
            self.network = self.netlist[-1]
            self.netlist = self.netlist[:-1]
            self.network = n
            # Log
            newname = self.network.name
            if newname == oldname:
                self.logger.info('Network saved: %s' %oldname)
            else:
                self.logger.info('Network %s saved as: %s' %(oldname, newname))

    def _load(self):
        n = Network()
        n.load()  # Open dialog
        if n.net is not None:
            self.netlist.append(n)
            self.network = n
            self.logger.info('Network loaded: %s' %n.name)
    
    def _load_input_data(self):
        self.input_data.configure_traits(view='all_view')

    def _load_target_data(self):
        self.target_data.configure_traits(view='all_view')
    
    def _export(self):
        raise NotImplementedError
    
    def _train_settings(self):
        self.edit_traits(view='settings_view', kind='modal')
        #self.train_algorithm.edit_traits(kind='modal')

    def _train(self):
        self.logger.info('Training network: %s' %self.network.name)
        self.logger.info("Using '%s' trainig algorithm." %self.train_algorithm.name)
        inp = self.input_data.load()
        trg = self.target_data.load()
        thread.start_new_thread(self.train_algorithm.train, (self.network.net, inp, trg, self.logs))
        time.sleep(0.1)  # Wait a while for ui to be updated (it may rely on train_algorithm values)
        self._garbage = 'a'
        #self.edit_traits(view = 'training_view', kind = 'livemodal')

    def _train_stop(self):
        self.train_algorithm.running.value = 0
        time.sleep(0.1)  # Wait a while for ui to be updated (it may rely on train_algorithm values)
        self._garbage = 'b'

    traits_view = View(UItem('network', emphasized=True, enabled_when='netlist'),
                       VSplit(Tabbed(UItem('object.network.info',
                                          style='readonly',
                                          label='Info'),
                                     UItem('object.network.preview_figure',
                                          style='custom',
                                          label='Architecture'),
                                    scrollable=True),
                              Tabbed(
                                     Item('logs', style='custom', height = 0.3),
                                     Item('values',
                                          label  = 'Shell',
                                          editor = ShellEditor( share = True ),
                                          dock   = 'tab',
                                          export = 'DockWindowShell'
                                          ),
                                     show_labels = False
                                    ),
                             ),
                       title = 'ffnet - neural network trainer',
                       width=0.4,
                       height=1.0,
                       resizable = True,
                       # menubar = menubar,
                       toolbar = toolbar,
                       )

    settings_view = View(Item('train_algorithm'),
                         Item('object.train_algorithm.maxfun'),
                         Item('object.train_algorithm.nproc'),
                         Item('object.train_algorithm.messages'),
                         buttons = ['OK', 'Cancel'],
                         title = 'Training settings',
                         width = 0.2,
                         )
    
    training_view = View(UItem('stop_training'),
                         title = 'Training network...',
                         width = 0.2)

if __name__=="__main__":
    from ffnet import loadnet, version
    import os
    t = Trainer()
    t.logger.info('Welcome! You are using ffnet-%s.' %version)
    # Add test network
    n = Network()
    path = 'testnet.net'
    n.net = loadnet(path)
    n.preview_figure.net = n.net
    n.file_name = path
    n.name = os.path.splitext(os.path.basename(path))[0]
    t.netlist.append(n)
    t.network = n
    # Add test data
    t.input_data.filename = 'black-scholes-input.dat'
    t.target_data.filename = 'black-scholes-target.dat'
    # Run
    t.configure_traits()

