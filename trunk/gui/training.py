from traits.api import *
from traitsui.api import *
import multiprocessing as mp
from process import Process
from redirfile import Redirector
import time
import numpy as np
from ffnet import ffnet, ffnetmodule
import logging
from plots.error_animation import ErrorAnimation
import thread


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

    def __repr__(self):
        return self.name

    def __init__(self, app=None, **traits):
        super(Trainer, self).__init__(**traits)
        self.app = app

    def _running_changed(self):
        self.app.shared.running.value = int(self.running)

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

    def assign_best_weights(self):
        self.app.network.net.weights[:] = self.app.shared.wlist[-1]

    def _train(self):
        logger = self.app.logs.logger
        logger.info('Using "%s" trainig algorithm.' %self.name)
        logger.info('Training in progress...')
        r = Redirector(fd=2)  # Redirect stderr
        r.start()
        t0 = time.time()
        if self.iteration == 0:  # we just started
            self._save_iteration()
        ## RUN 
        self.running = True
        self.setup()
        process = self.training_process()
        process.start()
        process.join()
        process.terminate()
        self.assign_best_weights()
        running_status = self.running  # Keep for logging
        self.running = False
        t1 = time.time()
        output = r.stop()
        self.app.plots.selected.stop()  # This is inside training thread
        ##
        # Log things
        logger.info(output.strip())
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
        self.app.plots.selected.start()  # for Qt this must be outside thread
        thread.start_new_thread(self._train, ())

    def setup(self):
        raise NotImplementedError

    def training_process(self):
        raise NotImplementedError

    def stopper(self):
        raise NotImplementedError


class TncTrainer(Trainer):
    name = Str('tnc')
    maxfun = Int(0)
    nproc =  Int(mp.cpu_count())
    messages = Int(1)

    def setup(self):
        if self.maxfun == 0:
            self.maxfun = max(100, 10*len(self.app.network.net.weights))  # should be in ffnet ?!
        self.nproc = min(self.nproc, len(self.app.data.input_t))  # should be in ffnet ?!
        import sys
        if sys.platform.startswith('win'):
            self.nproc = 1  # TODO, why nproc > 1 is so memory hungry?

    def stopper(self):
        if self.app.shared.running.value == 0:
            if self.nproc > 1:
                self.app.network.net._clean_mp()  # this raises AssertionError
            raise AssertionError

    def training_process(self):
        process = Process(target=self.app.network.net.train_tnc,
                          args=(self.app.data.input_t, self.app.data.target_t),
                          kwargs={'nproc':self.nproc,
                                  'maxfun': self.maxfun,
                                  'disp': self.messages,
                                  'callback': self.callback})
        return process



if __name__ == "__main__":
    from ffnet_import import *
    net = ffnet(mlgraph((2,2,1)))
    inp = [[0,0], [1,1], [1,0], [0,1]]
    trg = [[1], [1], [0], [0]]
    
    tnc = TncTrainer()
    #tnc.train(net, inp, trg, Logs())
