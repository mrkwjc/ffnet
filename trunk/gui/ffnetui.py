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
from mplplots import ErrorFigure

class Trainer(HasTraits):
    network = Instance(Network, ())
    input_data = Instance(LoadTxt, ())
    target_data = Instance(LoadTxt, ())
    trainer = Instance(TncTrainer, ())
    logs = Instance(Logger, ())
    running = Bool(False)
    logger = DelegatesTo('logs')
    net = DelegatesTo('network')
    inp = DelegatesTo('input_data', prefix='data')
    trg = DelegatesTo('target_data', prefix='data')
    error_figure = Instance(ErrorFigure, ())

    #def __init__(self, **traits):
        #HasTraits.__init__(self, **traits)        

    def _new(self):
        self.network.create(logger=self.logs.logger)

    def _load(self):
        self.network.load(logger=self.logs.logger)

    def _save_as(self):
        self.network.save_as(logger=self.logs.logger)

    def _export(self):
        raise NotImplementedError

    def _close(self):
        self.network.close(logger=self.logs.logger)
        self._reset()

    def _load_input_data(self):
        self.input_data.configure_traits(view='all_view', kind='modal')
        if self.inp_is_ok and self.input_data.updated:
            msg = "Loaded %i input patterns from file: %s" %(self.inp.shape[0],
                                                             self.input_data.filename)
            self.logs.logger.info(msg)
            self.input_data.updated = False

    def _load_target_data(self):
        self.target_data.configure_traits(view='all_view', kind='modal')
        if self.trg_is_ok and self.target_data.updated:
            msg = "Loaded %i target patterns from file: %s" %(self.trg.shape[0],
                                                              self.target_data.filename)
            self.logs.logger.info(msg)
            self.target_data.updated = False

    @property
    def inp_is_ok(self):
        if self.net and self.inp is not None:
            return self.inp.shape[1] == len(self.net.inno)
        return False

    @property
    def trg_is_ok(self):
        inp = self.inp
        trg = self.trg
        net = self.net
        if self.net and inp is not None and trg is not None:
            return trg.shape[1] == len(net.outno) and len(inp) == len(trg)
        return False

    def _train_settings(self):
        #self.edit_traits(view='settings_view', kind='modal')
        self.trainer.edit_traits(kind='modal')

    def _train(self):
        self.logger.info('Training network: %s' %self.network.filename)
        self.logger.info("Using '%s' trainig algorithm." %self.trainer.name)
        thread.start_new_thread(self.trainer.train, (self,))

    def _train_stop(self):
        self.trainer.running.value = 0

    def _reset(self):
        if self.net:
            self.net.randomweights()
            self.logger.info('Weights has been randomized!')
        self.trainer.reset()
        self.error_figure.reset()

    traits_view = View(#UItem('network', emphasized=True, enabled_when='netlist'),
                       VSplit(#Tabbed(UItem('object.network.info',
                                          #style='readonly',
                                          #label='Info'),
                                     #UItem('object.network.preview_figure',
                                          #style='custom',
                                          #label='Architecture'),
                                    #scrollable=True),
                        UItem('error_figure', style='custom'),
                              Tabbed(
                                     Item('logs', style='custom', height = 0.3, resizable = True),
                                     #Item('values',
                                          #label  = 'Shell',
                                          #editor = ShellEditor( share = True ),
                                          #dock   = 'tab',
                                          #export = 'DockWindowShell'
                                          #),
                                     show_labels = False
                                    )),
                             #),
                       title = 'ffnet - neural network trainer',
                       width=0.4,
                       height=0.8,
                       resizable = True,
                       #menubar = menubar,
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
    t.logs.logger.info('Welcome! You are using ffnet-%s.' %version)
    # Add test network
    n = t.network
    path = 'testnet.net'
    n.net = loadnet(path)
    #n.preview_figure.net = n.net
    n.filename = path
    #n.name = os.path.splitext(os.path.basename(path))[0]
    #t.netlist.append(n)
    #t.network = n
    # Add test data
    t.input_data.filename = 'black-scholes-input.dat'
    t.input_data.load()
    t.target_data.filename = 'black-scholes-target.dat'
    t.target_data.load()

    # Run
    t.configure_traits()

