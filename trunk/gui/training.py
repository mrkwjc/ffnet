# -*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

from traits.api import *
from traitsui.api import *
from ffnet import ffnetmodule
import multiprocessing as mp
from process import Process
from redirfile import Redirector
import time
import numpy as np
from threading import Thread
import sys


def parse_tnc_output(output):
    import cStringIO
    f = cStringIO.StringIO(output)
    res = np.loadtxt(f, skiprows=1)
    return res


class Trainer(HasTraits):
    app = Any
    name = Str
    running = Bool(False)
    iteration = Property(Int(0), transient=True)  # transient for non-pickling
    step = 1
    training_thread = Instance(Thread, transient=True)
    best_weights = Enum('minimum validation error', 'minimum training error', 'last iteration')
    maxfun = Range(low=0)

    def __repr__(self):
        return self.name

    def __init__(self, app=None, **traits):
        super(Trainer, self).__init__(**traits)
        self.app = app

    def _running_changed(self, old, new):
        self.app.shared.running.value = int(new)
        #if new and not old: # we are starting training
        #if old and not new:  # we finished training

    def _get_iteration(self):
        return self.app.shared.iteration.value

    def _set_iteration(self, value):
         self.app.shared.iteration.value = value

    def _save_iteration(self):
        w = self.app.network.net.weights[:]
        e = self.error_t()
        v = self.error_v()
        i = self.iteration
        if not i%self.step:
            self.app.shared.wlist.append(w)
            self.app.shared.tlist.append(e)
            if v is not None:
                self.app.shared.vlist.append(v)
            self.app.shared.ilist.append(i)
        self.assign_best_weights()
        self.iteration += 1

    def sqerror(self, inp, trg):
        net = self.app.network.net
        err = ffnetmodule.netprop.sqerror
        e  = err(net.weights, net.conec, net.units, net.inno, net.outno, inp, trg)
        return e

    def error_t(self):
        inp = self.app.data.input_t_n
        trg = self.app.data.target_t_n
        return self.sqerror(inp, trg)

    def error_v(self):
        inp = self.app.data.input_v_n
        trg = self.app.data.target_v_n
        if len(inp):
            return self.sqerror(inp, trg)
        else:
            return None

    def callback(self, x):  # This is called in child process
        self.app.network.net.weights[:] = x
        self._save_iteration()
        self.stopper()  # This is actually the only way to stop C based optimizer

    def _train(self):
        logger = self.app.logs.logger
        logger.info('Using "%s" trainig algorithm.' %self.name)
        logger.info('Training in progress...')
        #r = Redirector(fd=2)  # Redirect stderr
        #r.start()
        t0 = time.time()
        ## RUN 
        # Be sure network and data are normalized
        self.app.data.normalize = self.app.network.net.renormalize
        self.app.data._normalize_data()
        # Always start with last weights
        if self.iteration > 0:
            self.app.network.net.weights[:] = self.app.shared.wlist[-1]
        self.running = True
        self.setup()
        process = self.training_process()
        process.start()
        if self.iteration == 0:  # we just started, save initial state
            self._save_iteration()
        process.join()
        if isinstance(process, Process):
            process.terminate()
        self.assign_best_weights()
        running_status = self.running  # Keep for logging
        self.running = False
        t1 = time.time()
        #output = r.stop()
        self.app.plots.stop()  # This is inside training thread
        ##
        # Log things
        #logger.info(output.strip())
        if not running_status:
            logger.info('Training stopped by user.')
        else:
            if not process.exception:
                logger.info('Training finished normally.')
            else:
                err, tb = process.exception
                logger.info('Training finished with error:')
                logger.info(tb.strip())
        logger.info('Execution time: %3.3f seconds.' %(t1-t0))

    def train(self):
        self.app.plots.start()  # for Qt this must be outside thread
        self.training_thread = Thread(target = self._train)
        self.training_thread.start()

    def setup(self):
        pass

    def training_process(self):
        raise NotImplementedError

    def stopper(self):
        raise NotImplementedError

    @on_trait_change('app.network.net')
    def estimate_maxfun(self):
        if self.app is not None and self.app.network.net is not None:
            self.maxfun = max(100, 10*len(self.app.network.net.weights))  # Set default value

    @on_trait_change('best_weights')
    def assign_best_weights(self):
        if self.iteration == 0:  # nothing to assign
            return
        idx = self.app.shared.bwidx.value
        if self.best_weights == 'last iteration':
            idx = len(self.app.shared.tlist) - 1
        if self.best_weights == 'minimum training error' or len(self.app.shared.vlist) == 0:
            if self.running:  # speed up things (argmin costs time)
                if self.app.shared.tlist[idx] > self.app.shared.tlist[-1]:
                    idx = len(self.app.shared.tlist) - 1
            else:
                idx = np.argmin(self.app.shared.tlist)
        if self.best_weights == 'minimum validation error' and len(self.app.shared.vlist) > 0:
            if self.running:  # speed up things (argmin costs time)
                if self.app.shared.vlist[idx] > self.app.shared.vlist[-1]:
                    idx = len(self.app.shared.vlist) - 1
            else:
                idx = np.argmin(self.app.shared.vlist)
        self.app.shared.bwidx.value = idx
        self.app.network.net.weights[:] = self.app.shared.wlist[idx]


class TncTrainer(Trainer):
    name = Str('tnc')
    nproc =  Enum(range(mp.cpu_count(), 0, -1))  #(low=1, high=mp.cpu_count(), value=mp.cpu_count())

    def __init__(self, **traits):
        super(TncTrainer, self).__init__(**traits)
        if sys.platform.startswith('win'):  # Set default nproc to 1 on windows
            self.nproc = 1

    @on_trait_change('app.data.status')
    def check_nproc(self):
        if self.app is not None and self.app.data.status in [1,2] and len(self.app.data.input_t) > 0:
            self.nproc = min(self.nproc, len(self.app.data.input_t))

    #def setup(self):
        #if self.maxfun == 0:
            #self.maxfun = max(100, 10*len(self.app.network.net.weights))
        #self.nproc = min(self.nproc, len(self.app.data.input_t))

    def stopper(self):
        if self.app.shared.running.value == 0:
            if self.nproc > 1:
                self.app.network.net._clean_mp()  # this raises AssertionError
            raise AssertionError

    def training_process(self):
        # self.app.trait('plist').transient = True  #Why this not works on 'selected'?
        # if sys.platform.startswith('win') and self.nproc == 1:
        #     from threading import Thread as Process
        process = Process(target=self.app.network.net.train_tnc,
                          args=(self.app.data.input_t, self.app.data.target_t),
                          kwargs={'nproc':self.nproc,
                                  'maxfun': self.maxfun,
                                  'disp': 0,
                                  'callback': self.callback})
        return process

    traits_view = View(Item('maxfun'),
                       Item('nproc'),
                       resizable=True)


class BfgsTrainer(Trainer):
    name = Str('bfgs')

    #def setup(self):
        #if self.maxfun == 0:
            #self.maxfun = max(100, 10*len(self.app.network.net.weights))

    def stopper(self):
        if self.app.shared.running.value == 0:
            raise AssertionError

    def training_process(self):
        process = Process(target=self.app.network.net.train_bfgs,
                          args=(self.app.data.input_t, self.app.data.target_t),
                          kwargs={'maxfun': self.maxfun,
                                  'disp': 0,
                                  'callback': self.callback})
        return process

    traits_view = View(Item('maxfun'),
                       resizable=True)


class CgTrainer(Trainer):
    name = Str('cg')

    #def setup(self):
        #if self.maxiter == 0:
            #self.maxiter = max(100, 10*len(self.app.network.net.weights))

    def stopper(self):
        if self.app.shared.running.value == 0:
            raise AssertionError

    def training_process(self):
        process = Process(target=self.app.network.net.train_cg,
                          args=(self.app.data.input_t, self.app.data.target_t),
                          kwargs={'maxiter': self.maxfun,
                                  'disp': 0,
                                  'callback': self.callback})
        return process

    traits_view = View(Item('maxfun', label='Maxiter'),
                       resizable=True)


if __name__ == "__main__":
    from ffnet import *
    net = ffnet(mlgraph((2,2,1)))
    inp = [[0,0], [1,1], [1,0], [0,1]]
    trg = [[1], [1], [0], [0]]
    
    tnc = TncTrainer()
    tnc.configure_traits()
    #tnc.train(net, inp, trg, Logs())
