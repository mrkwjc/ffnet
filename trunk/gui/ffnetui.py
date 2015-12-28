#-*- coding: utf-8 -*-
## from traits.etsconfig.api import ETSConfig
## ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *
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
from animations import *
from plots.mplfigure import MPLPlotter

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
    plist = List([ErrorAnimation(), TOAnimation(), GraphAnimation()], value=MPLPlotter, transient=True) 
    selected = Instance(MPLPlotter, transient=True)  # Cannot be pickled when animation runs
    shell = PythonValue(Dict)
    running = DelegatesTo('trainer')
    net = DelegatesTo('network')
    data_status = DelegatesTo('data',  prefix='status')

    #_progress = Property(depends_on='plots.training_in_progress._progress')

    #def _get__progress(self):
        #return self.plots.training_in_progress._progress

    #def __getstate__(self):
        ## managers, loggers and figures are not picklable
        #self.shared.manager = None
        #state = self.__dict__.copy()
        #del state['logs']
        #del state['plots']
        #return state

    def __init__(self, **traits):
        super(FFnetApp, self).__init__(**traits)
        self.network.app = self
        self.data.app = self
        self.data.input_loader.app = self
        self.data.target_loader.app = self
        self.trainer.app = self
        for p in self.plist:
            p.app = self
            p.interval=500
        self.selected = self.plist[0]
        #self.plots.app = self
        #self.plots.selected = self.plots.plist[0]
        self.shell = {'app':self}

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
        self.logs.logger.info('Training network: %s' %self.network.filename)
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

    def _selected_changed(self, old, new):
        if self.trainer.running:
            try:
                # Assume we have animation
                old.stop()
            except:
                # But simple plot can be also
                pass
            try:
                # Assume we have animation
                new.start()
            except:
                # But simple plot can be also
                new.replot()
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
    t.data.input_loader.load()
    t.data.target_loader.filename = 'data/black-scholes-target.dat'
    t.data.target_loader.load()

    # Run
    t.configure_traits()

