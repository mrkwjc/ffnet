from enthought.traits.api import *
from enthought.traits.ui.api import *
import multiprocessing as mp
from process import Process
from redirfile import Redirector
import time
from exceptions import Exception
import numpy as np


def parse_tnc_output(output):
    import cStringIO
    f = cStringIO.StringIO(output)
    res = np.loadtxt(f, skiprows=1)
    return res

class TrainigStopped(Exception):
    def __init__(self, message = "Training stopped by user."):
        super(TrainigStopped, self).__init__(message)

class Trainer(HasTraits):
    name = Str
    running = Instance(mp.Value, ('i', 0))  # shared memory value

    def __repr__(self):
        return self.name

class TncTrainer(Trainer):
    name = Str('tnc')
    maxfun = Int(0)
    nproc =  Int(mp.cpu_count())
    messages = Int(1)
    elist = List([])
    vlist = List([])
    manager = Any
    wlist = Any
    continued = Int(0)

    def __init__(self, **traits):
        HasTraits.__init__(self, **traits)
        self.manager = mp.Manager()
        self.wlist = self.manager.list([])

    def reset(self):
        self.wlist = self.manager.list([])
        self.elist = []
        self.vlist = []
        self.continued = 0

    #def tsqerror(self):
        #w0 = self.net.weights
        #for w in self.wlist:
            #self.net.weights = w
            #e = self.net.sqerror(self.inpt, self.trgt)
            #self.elist.append(e)
        #self.net.weights = w0
    
    def vsqerror(self):
        if len(self.inpv)>0:
            w0 = self.net.weights[:]
            for w in self.wlist[self.continued:]:
                self.net.weights[:] = w
                v = self.net.sqerror(self.inpv, self.trgv)
                self.vlist.append(v)
            self.net.weights[:] = w0

    # Is this a good place for doing all this?
    def _callback(self, x):
        self.wlist.append(x)
        if self.running.value == 0:
            if self.nproc > 1:
                self.net._clean_mp()  # this raises AssertionError
            raise AssertionError

    def train(self, info):
        # Setup
        logger = info.logger
        net = info.net
        inp = info.inp
        trg = info.trg
        net.renormalize = info.normalize
        net._setnorm(inp, trg)  # this sets
        info.normalize = net.renormalize
        vmask = info.vmask
        self.inpt = inp[~vmask]
        self.trgt = trg[~vmask]
        self.inpv = inp[vmask]
        self.trgv = trg[vmask]
        self.net = net
        if not self.maxfun:
            self.maxfun = max(100, 10*len(net.weights))  # should be in ffnet!
        self.nproc = min(self.nproc, len(self.inpt))  # should be in ffnet!
        #
        ## Run training
        info.logs.progress_start("Training in progress...")
        info.plots.is_training = True
        #logger.info("Training in progress. Please wait ...")
        r = Redirector(fd=2)  # Redirect stderr
        r.start()
        t0 = time.time()
        self.running.value = 1
        info.running = True
        if not self.continued:
            self.wlist.append(net.weights)
        process = Process(target=net.train_tnc,
                          args=(self.inpt, self.trgt),
                          kwargs={'nproc':self.nproc,
                                  'maxfun': self.maxfun,
                                  'disp': self.messages,
                                  'callback': self._callback})
        process.start()
        process.join()
        process.terminate()
        net.weights[:] = self.wlist[-1]
        running = self.running.value  # Keep for logging
        self.running.value = 0
        info.running = False
        t1 = time.time()
        info.logs.progress_stop()
        ## Training finished
        #
        # Get catched output
        output = r.stop()
        err = parse_tnc_output(output).T[2].tolist()
        if self.continued:
            err = err[1:]
        if not running:
            err = err[:-1]
        self.elist += err
        self.vsqerror()
        info.plots.training_error = self.elist
        info.plots.validation_error = self.vlist
        #info.plots.error.reset()
        #info.plots.error.plot(range(len(self.elist)), self.elist)
        #info.plots.error.plotv(range(len(self.vlist)), self.vlist)
        logger.info(output.strip())
        info.plots.is_training = False
        # Discover and log reason of termination
        if not running:
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
        self.continued = len(self.wlist)


    traits_view = View(
                       Item('maxfun'),
                       Item('nproc'),
                       Item('messages'),
                       buttons = ['OK', 'Cancel'],
                       title = 'Tnc training options',
                       width = 0.2,
                       )

if __name__ == "__main__":
    from ffnet_import import *
    net = ffnet(mlgraph((2,2,1)))
    inp = [[0,0], [1,1], [1,0], [0,1]]
    trg = [[1], [1], [0], [0]]
    class Logs:
        import logging
        logger = logging.Logger('test', level=logging.DEBUG)
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        def progress_start(self, msg): pass
        def progress_stop(self): pass


    tnc = TncTrainer()
    tnc.train(net, inp, trg, Logs())
