#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from enthought.traits.api import *
from enthought.traits.ui.api import *
from pyface.api import GUI
from data import TrainingData
from network import Network
from training import TncTrainer
import sys
import time
import uuid

import thread
from logger import Logger
from actions import toolbar, menubar
#from plots.error_animation import ErrorAnimation
#from plots.to_animation import TOAnimation
from animations import Plots

import multiprocessing as mp
from shared import Shared
import numpy as np

class TrainingSettings(HasTraits):
    training_algorithm = Enum('tnc')
    # tnc options
    maxfun = Int(0)
    nproc = Int(mp.cpu_count())
    # other
    validation_patterns = Range(0, 50, 10)  # %
    validation_type = Enum('random', 'last')
    normalize = Bool(True)

    traits_view = View(Item('training_algorithm'),
                       Item('maxfun', visible_when='training_algorithm == "tnc"'),
                       Item('nproc', visible_when='training_algorithm == "tnc"'),
                       Item('validation_patterns', label = 'Validation patterns [%]'),
                       Item('validation_type'),
                       Item('normalize'),
                       buttons = ['OK', 'Cancel'],
                       title = 'Training settings',
                       resizable = True,
                       width = 0.2)

class FFnetApp(HasTraits):
    network = Instance(Network, ())
    data = Instance(TrainingData, ())
    shared = Instance(Shared, ())
    trainer = Instance(TncTrainer, ())
    settings = Instance(TrainingSettings, ())
    logs = Instance(Logger, ())
    running = DelegatesTo('trainer')
    logger = DelegatesTo('logs')
    net = DelegatesTo('network')
    normalize = DelegatesTo('settings')
    data_status = DelegatesTo('data', prefix='status')
    plots = Instance(Plots, ())
    #plot = Instance(TOAnimation, ())

    #_progress = Property(depends_on='plots.training_in_progress._progress')

    #def _get__progress(self):
        #return self.plots.training_in_progress._progress

    def __init__(self, **traits):
        super(FFnetApp, self).__init__(**traits)
        self.data.app = self
        self.data.input_loader.app = self
        self.data.target_loader.app = self
        self.trainer.app = self
        self.plots.app = self
        self.plots.selected = self.plots.plist[0]

    def _new(self):
        self.network.create(logger=self.logs.logger)
        self.normalize = self.net.renormalize

    def _load(self):
        self.network.load(logger=self.logs.logger)
        self.normalize = self.net.renormalize

    def _save_as(self):
        self.network.save_as(logger=self.logs.logger)

    def _export(self):
        raise NotImplementedError

    def _close(self):
        self.network.close(logger=self.logs.logger)
        self._reset()

    def _load_data(self):
        self.data.edit_traits(kind='livemodal')

    def _train_settings(self):
        #self.edit_traits(view='settings_view', kind='modal')
        self.settings.edit_traits(kind='livemodal')

    def _train_start(self):
        self.logger.info('Training network: %s' %self.network.filename)
        self.trainer.train()

    def _train_stop(self):
        self.trainer.running = False

    def _reset(self):
        if self.net:
            self.net.randomweights()
            self.logger.info('Weights has been randomized!')
        self.trainer.__init__()
        self.plots.plot_init()
        self.plots.figure.draw()

    def _normalize_changed(self):
        self.net.renormalize = self.normalize

    traits_view = View(VSplit(UItem('object.plots', style='custom'),
                              Tabbed(UItem('logs', style='custom', dock = 'tab', height = 0.25),
                                     #Item('values',
                                          #label  = 'Shell',
                                          #editor = ShellEditor( share = True ),
                                          #dock   = 'tab',
                                          #export = 'DockWindowShell'
                                          #),
                                     #show_labels = False
                                    )
                              ),
                             #),
                       title = 'ffnet - neural network trainer',
                       width=0.6,
                       height=0.8,
                       resizable = True,
                       #menubar = menubar,
                       toolbar = toolbar,
                       #statusbar = [StatusItem(name = '_progress', width=200)]
                       )
    
    training_view = View(UItem('stop_training'),
                         title = 'Training network...',
                         width = 0.2)

if __name__=="__main__":
    from ffnet import loadnet, version
    import os
    t = FFnetApp()
    t.logs.logger.info('Welcome! You are using ffnet-%s.' %version)
    # Add test network
    n = t.network
    path = 'data/testnet.net'
    n.net = loadnet(path)
    #n.preview_figure.net = n.net
    n.filename = path
    #n.name = os.path.splitext(os.path.basename(path))[0]
    #t.netlist.append(n)
    #t.network = n
    # Add test data
    t.data.input_loader.filename = 'data/black-scholes-input.dat'
    t.data.input_loader.load()
    t.data.target_loader.filename = 'data/black-scholes-target.dat'
    t.data.target_loader.load()

    # Run
    t.configure_traits()

