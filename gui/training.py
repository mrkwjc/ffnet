from enthought.traits.api import *
from enthought.traits.ui.api import *
import multiprocessing as mp
from process import Process
from redirfile import Redirector
import time


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

    # Is this good place for doing this?
    def _callback(self, x):
        if self.running.value == 0:
            self.net.weights[:] = x  #TODO: weights are not saved!
            # If multiprocessing is used in fmin_tnc we need to terminate these processes
            if self.nproc > 1:
                self.net._clean_mp()  # this raises AssertionError
            raise AssertionError

    def train(self, net, inp, trg, logs):
        # Setup
        logger = logs.logger
        self.net = net
        if not self.maxfun:
            self.maxfun = max(100, 10*len(net.weights))  # should be in ffnet!
        self.nproc = min(self.nproc, len(inp))  # should be in ffnet!
        #
        ## Run training
        logs.progress_start("Training in progress...")
        r = Redirector(fd=2)  # Redirect stderr
        r.start()
        t0 = time.time()
        self.running.value = 1
        process = Process(target=net.train_tnc,
                               args=(inp, trg),
                               kwargs={'nproc':self.nproc,
                                       'maxfun': self.maxfun,
                                       'disp': self.messages,
                                       'callback': self._callback})
        process.start()
        process.join()
        process.terminate()
        running = self.running.value  # Keep for logging
        self.running.value = 0
        t1 = time.time()
        logs.progress_stop()
        ## Training finished
        #
        # Get catched output
        output = r.stop()
        logger.info(output.strip())
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
