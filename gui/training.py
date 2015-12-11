from enthought.traits.api import *
from enthought.traits.ui.api import *
import multiprocessing as mp
from process import Process
from redirfile import Redirector
import time
import numpy as np
from ffnet import ffnet, ffnetmodule
import logging
from plots.error_animation import ErrorAnimation

def parse_tnc_output(output):
    import cStringIO
    f = cStringIO.StringIO(output)
    res = np.loadtxt(f, skiprows=1)
    return res

class Trainer(HasTraits):
    name = Str
    #manager = Instance(mp.Manager)
    net = Any(ffnet)
    input = CArray()
    target = CArray()
    input_v = CArray()
    target_v = CArray()
    iteration = Int(0)
    logger = Instance(logging.Logger)
    running = Bool(False)

    def __repr__(self):
        return self.name

    def __init__(self, **traits):
        super(Trainer, self).__init__(**traits)
        self.manager = mp.Manager()
        self.condition = self.manager.Condition()
        #self.common = self.manager.Namespace()
        self.mprunning = mp.Value('i', 0)
        self.wlist = self.manager.list([])
        self.elist = self.manager.list([])
        self.vlist = self.manager.list([])
        self.ilist = self.manager.list([]) # integers
        self.logger = logging.getLogger()
        self.iteration = 0

    def _running_changed(self):
        self.mprunning.value = self.running
        if len(self.ilist):
            self.iteration = self.ilist[-1]
            self.net.weights[:] = self.wlist[-1]

    def _set_normalized_data(self):
        self.net._setnorm(np.vstack([self.input, self.input_v]),
                          np.vstack([self.target, self.target_v]))  # First set parameters
        self.input_n, self.target_n = self.net._setnorm(self.input, self.target)
        if len(self.input_v) > 0:
            self.input_v_n, self.target_v_n = self.net._setnorm(self.input_v, self.target_v)

    def _sqerror(self, inp, trg):
        err = ffnetmodule.netprop.sqerror
        e  = err(self.net.weights, self.net.conec, self.net.units,
                 self.net.inno, self.net.outno, inp, trg)
        return e

    def save_iteration(self):
        e = self._sqerror(self.input_n, self.target_n)
        #e = self.net.sqerror(self.input, self.target)
        if len(self.input_v) > 0:
            v = self._sqerror(self.input_v_n, self.target_v_n)
            #v = self.net.sqerror(self.input_v, self.target_v)
        #with self.condition:   # plots are using this data, we need to synchronize
        self.ilist.append(self.iteration)
        self.wlist.append(self.net.weights)
        self.elist.append(e)
        if len(self.input_v) > 0:
            self.vlist.append(v)
        self.iteration += 1
        #self.condition.notify_all()

    def callback(self, x):  # This will be called in child process
        self.net.weights = x
        self.save_iteration()
        self.stopper()


class TncTrainer(Trainer):
    name = Str('tnc')
    maxfun = Int(0)
    nproc =  Int(mp.cpu_count())
    messages = Int(1)

    def _net_changed(self):
        if self.maxfun == 0:
            self.maxfun = max(100, 10*len(self.net.weights))  # should be in ffnet ?!

    def _input_changed(self):
        self.nproc = min(self.nproc, len(self.input))  # should be in ffnet ?!

    def stopper(self):
        if self.mprunning.value == 0:
            if self.nproc > 1:
                self.net._clean_mp()  # this raises AssertionError
            raise AssertionError
    
    def train(self):  # run this is separate thread !
        logger = self.logger
        logger.info("Training in progress...")
        r = Redirector(fd=2)  # Redirect stderr
        r.start()
        t0 = time.time()
        self.running =  True
        self.mprunning.value = True
        self._set_normalized_data()  # be sure normalized data are correct before training
        if self.iteration == 0:  # we just started
            self.save_iteration()
        self._net_changed()  # HACK for maxfun
        process = Process(target=self.net.train_tnc,
                          args=(self.input, self.target),
                          kwargs={'nproc':self.nproc,
                                  'maxfun': self.maxfun,
                                  'disp': self.messages,
                                  'callback': self.callback})
        process.start()
        process.join()
        process.terminate()
        self.net.weights[:] = self.wlist[-1]
        running_status = self.mprunning.value  # Keep for logging
        self.running = False
        t1 = time.time()
        output = r.stop()
        self.plot.stop()
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
        # Log time
        logger.info('Execution time: %3.3f seconds.' %(t1-t0))


if __name__ == "__main__":
    from ffnet_import import *
    net = ffnet(mlgraph((2,2,1)))
    inp = [[0,0], [1,1], [1,0], [0,1]]
    trg = [[1], [1], [0], [0]]
    
    tnc = TncTrainer()
    #tnc.train(net, inp, trg, Logs())
