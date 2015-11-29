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

from logger import Logger
from bars import toolbar, menubar
from plots.error_plot import ErrorPlot as Plots

import multiprocessing as mp
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


class FFnetRoot(HasTraits):
    network = Instance(Network, ())
    input_data = Instance(LoadTxt, ())
    target_data = Instance(LoadTxt, ())
    trainer = Instance(TncTrainer, ())
    settings = Instance(TrainingSettings, ())
    logs = Instance(Logger, ())
    running = Bool(False)
    logger = DelegatesTo('logs')
    net = DelegatesTo('network')
    inp = DelegatesTo('input_data', prefix='data')
    trg = DelegatesTo('target_data', prefix='data')
    validation_patterns = DelegatesTo('settings')
    validation_type = DelegatesTo('settings')
    normalize = DelegatesTo('settings')
    plots = Instance(Plots, ())

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

    def _load_input_data(self):
        self.input_data.configure_traits(view='all_view', kind='modal')
        if self.inp_is_ok and self.input_data.updated:
            msg = "Loaded %i input patterns from file: %s" %(self.inp.shape[0],
                                                             self.input_data.filename)
            self.logs.logger.info(msg)
            self.input_data.updated = False
            self._set_validation_mask()


    def _load_target_data(self):
        self.target_data.configure_traits(view='all_view', kind='modal')
        if self.trg_is_ok and self.target_data.updated:
            msg = "Loaded %i target patterns from file: %s" %(self.trg.shape[0],
                                                              self.target_data.filename)
            self.logs.logger.info(msg)
            self.target_data.updated = False
            self._set_validation_mask()

    @property
    def inp_is_ok(self):
        if self.net and len(self.inp) > 0:
            return self.inp.shape[1] == len(self.net.inno)
        return False

    @property
    def trg_is_ok(self):
        inp = self.inp
        trg = self.trg
        net = self.net
        if self.net and len(inp) > 0 and len(trg) > 0:
            return trg.shape[1] == len(net.outno) and len(inp) == len(trg)
        return False

    def _train_settings(self):
        #self.edit_traits(view='settings_view', kind='modal')
        self.settings.edit_traits(kind='modal')

    def _train(self):
        self.logger.info('Training network: %s' %self.network.filename)
        self.logger.info("Using '%s' trainig algorithm." %self.trainer.name)
        self.plots.selected = 'error'
        thread.start_new_thread(self.trainer.train, (self,))

    def _train_stop(self):
        self.trainer.running.value = 0

    def _reset(self):
        if self.net:
            self.net.randomweights()
            self.logger.info('Weights has been randomized!')
        self.trainer.reset()
        self.error_figure.reset()

    def _set_validation_mask(self):
        npat = len(self.inp)
        self.vmask = ~np.ones(npat, np.bool)
        if self.trg_is_ok:
            percent = self.settings.validation_patterns
            npat_v = percent*npat/100
            type_ = self.validation_type
            if type_ == 'random':
                idx = np.random.choice(npat, npat_v)
                mask = np.in1d(np.arange(npat), idx)
                self.vmask = mask
            if type_ == 'last':
                mask = np.ones(npat, np.bool)
                mask[:npat-npat_v] = False
                self.vmask = mask
            self.logger.info('%i training patterns chosen for validation (%s)' %(npat_v, type_))

    def _validation_patterns_changed(self):
        self._set_validation_mask()

    def _validation_type_changed(self):
        self._set_validation_mask()

    traits_view = View(VSplit(UItem('object.network.creator.preview_figure.figure', style='custom'),
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
                       )
    
    training_view = View(UItem('stop_training'),
                         title = 'Training network...',
                         width = 0.2)

if __name__=="__main__":
    from ffnet import loadnet, version
    import os
    t = FFnetRoot()
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
    t.input_data.filename = 'data/black-scholes-input.dat'
    t.input_data.load()
    t.target_data.filename = 'data/black-scholes-target.dat'
    t.target_data.load()
    t._set_validation_mask()

    # Run
    t.configure_traits()

