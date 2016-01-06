#-*- coding: utf-8 -*-
## from traits.etsconfig.api import ETSConfig
## ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *
from pyface.api import GUI
from data import TrainingData
from network import Network
from training import *
import sys
import time
import uuid

import thread
from logger import Logger
from actions import toolbar, menubar
from animations import *
from plots.mplfigure import MPLPlotter

import multiprocessing as mp
from shared import Shared
import numpy as np


class FFnetApp(HasTraits):
    network = Instance(Network)
    data = Instance(TrainingData)
    trainer = Instance(Trainer)
    shared = Instance(Shared, ())
    logs = Instance(Logger, ())
    plist = List([ErrorAnimation(), TOAnimation(), GraphAnimation()], value=MPLPlotter, transient=True) 
    selected = Instance(MPLPlotter, transient=True)  # Cannot be pickled when animation runs
    shell = PythonValue(Dict)
    mode = Enum('train', 'test', 'recall')
    algorithm = Enum('tnc', 'bfgs', 'cg')

    running = DelegatesTo('trainer')
    net = DelegatesTo('network')
    data_status = DelegatesTo('data',  prefix='status')

    #_progress = Property(depends_on='plots.training_in_progress._progress')

    #def _get__progress(self):
        #return self.plots.training_in_progress._progress

    def __init__(self, **traits):
        super(FFnetApp, self).__init__(**traits)
        self.network = Network(app = self)
        self.data = TrainingData(app = self)
        self.trainer = TncTrainer(app = self) # default trainer
        for p in self.plist:
            p.app = self
            p.interval=500
        self.selected = self.plist[0]
        self.shell = {'app':self}

    def _new(self):
        self.network.create()
        # self.normalize = self.net.renormalize

    def _load(self):
        self.network.load()
        # self.normalize = self.net.renormalize

    def _save_as(self):
        self.network.save_as()

    def _export(self):
        raise NotImplementedError

    def _close(self):
        self.network.close()
        self._reset()

    def _load_data(self):
        self.data.edit_traits(kind='livemodal')

    def _train_settings(self):
        #self.edit_traits(view='settings_view', kind='modal')
        self.edit_traits(view='settings_view', kind='livemodal')

    def _train_start(self):
        self.logs.logger.info('Training network: %s' %self.network.filename)
        self.trainer.train()

    def _train_stop(self):
        self.trainer.running = False

    def _reset(self):
        if self.net:
            self.net.randomweights()
            self.logs.logger.info('Weights has been randomized!')
        self.shared.populate() 
        self.selected.replot()

    def _algorithm_changed(self, new):
        if new == 'tnc':
            self.trainer = TncTrainer(app=self)
        if new == 'cg':
            self.trainer = CgTrainer(app=self)
        if new == 'bfgs':
            self.trainer = BfgsTrainer(app=self)

    def _selected_changed(self, old, new):
        if self.trainer.running:
            try:
                old.stop()  # Assume we have animation
            except:
                pass  # But simple plot can be also
            try:
                new.start()  # Assume we have animation
            except:
                new.replot()  # But simple plot can be also
        else:
            new.replot()

    traits_view = View(VSplit(Item('plist',
                            style='custom',
                            show_label=False,
                            height = 0.75,
                            editor=ListEditor(use_notebook=True,
                                              deletable=False,
                                              dock_style='tab',
                                              selected='selected',
                                              view = 'figure_view',
                                              page_name = '.name')),
                              Tabbed(UItem('logs',
                                           style='custom',
                                           dock = 'tab',
                                           export = 'DockWindowShell'),
                                     UItem('shell',
                                           label  = 'Shell',
                                           editor = ShellEditor( share = True ),
                                           dock   = 'tab',
                                           export = 'DockWindowShell'
                                           ),
                                     #show_labels = False
                                    )
                              ),
                             #),
                       title = 'ffnet - neural network trainer',
                       width = 0.6,
                       height = 0.8,
                       resizable = True,
                       #menubar = menubar,
                       toolbar = toolbar,
                       #statusbar = [StatusItem(name = '_progress', width=200)]
                       )

    settings_view = View(Item('mode', emphasized=True), 
                         Tabbed(
                         Group(Item('object.data.input_loader',
                                     style='custom',
                                     label='Input file',),
                                 Item('object.data.target_loader',
                                     style='custom',
                                     label='Target file'),
                                 Item('object.data.validation_patterns',
                                     label = 'Validation patterns [%]'),
                                 Item('object.data.validation_type'),
                                 Item('object.data.normalize'),
                                 visible_when = 'mode == "train"',
                                 label = 'Data'),
                         Group(Item('object.data.input_loader',
                                     style='custom',
                                     label='Input',),
                                 Item('object.data.target_loader',
                                     style='custom',
                                     label='Target'),
                                 visible_when = 'mode == "test"',
                                 label = 'Data'),
                         Group(Item('object.data.input_loader',
                                     style='custom',
                                     label='Input',),
                                 visible_when = 'mode == "recall"',
                                 label = 'Data'),
                         Group(Item('algorithm'), 
                                 UItem('object.trainer', style='custom'),
                                 visible_when='mode == "train"',
                                 label = 'Training')
                         ),
                         buttons = ['OK', 'Cancel'],
                         title = 'Settings...',
                         resizable = True,
                         width = 0.4)

    training_view = View(UItem('stop_training'),
                         title = 'Training network...',
                         width = 0.2)

if __name__=="__main__":
    from ffnet import loadnet, version
    import os
    mp.freeze_support()
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
    #t.data.input_loader.load()
    t.data.target_loader.filename = 'data/black-scholes-target.dat'
    #t.data.target_loader.load()

    # Run
    t.configure_traits()

