from enthought.traits.api import *
from enthought.traits.ui.api import *
import multiprocessing as mp
from process import Process
from redirfile import Redirector
import time


class Trainer(HasTraits):
    name = Str
    process = Instance(Process)
    running = Instance(mp.Value, ('i', 0))

    def __repr__(self):
        return self.name

class TncTrainer(Trainer):
    name = Str('tnc')
    maxfun = Int(0)
    nproc =  Int(1) #Int(mp.cpu_count())
    messages = Int(1)

    # Is this good place for doing this?
    def _callback(self, x):
        if self.running.value == 0:
            self.net.weights[:] = x  #TODO: weights are not saved!
            # If multiprocessing is used in fmin_tnc we need to terminate also these processes
            if self.nproc > 1:
                self.net._clean_mp()  # this raises AssertionError
            raise AssertionError

    def train(self, net, inp, trg, logger):
        # Setup
        self.net = net
        if not self.maxfun:
            self.maxfun = max(100, 10*len(net.weights))  # should be in ffnet!
        self.nproc = min(self.nproc, len(inp))  # should be in ffnet!
        # Redirect stderr
        r = Redirector(fd=2)
        r.start()
        ## Run training
        t0 = time.time()
        self.running.value = 1
        self.process = Process(target=net.train_tnc,
                               args=(inp, trg),
                               kwargs={'nproc':self.nproc,
                                       'maxfun': self.maxfun,
                                       'disp': self.messages,
                                       'callback': self._callback})
        self.process.start()
        self.process.join()
        # self.process.terminate()
        running = self.running.value  # Keep for logging
        self.running.value = 0
        t1 = time.time()
        ## Training finished
        # Get catched output and recover stderr
        output = r.stop()

        # Discover reason of termination
        if not running:
            # Training was finished by setting self.running.value = 0
            reason = 'Training stopped by user.'
        else:
            if not self.process.exception:
                reason = 'Training finished normally.'
            else:
                err, tb = self.process.exception
                reason = 'Training finished with error:\n\n'
                reason += tb
        # Log results
        #output += '\n' + reason
        #output += '\n' + 'Execution time: %3.3f seconds\n\n' %(t1-t0)
        #logger.info(output)  # Flush output in one logger call
        #logger.info(reason)
        #logger.info('Execution time: %3.3f seconds\n\n' %(t1-t0))
        #logger.info(output)  # Flush output in one logger call
        #logger.info(reason)
        #logger.info('Execution time: %3.3f seconds\n\n' %(t1-t0))
        logger(output)  # Flush output in one logger call
        logger(reason)
        logger('Execution time: %3.3f seconds\n' %(t1-t0))
        #logger(output)  # Flush output in one logger call
        #logger(reason)
        #logger('Execution time: %3.3f seconds\n\n' %(t1-t0))
        #time.sleep(0.1)
        # NEEDED logging facility, the above crashes gui sometimes!

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
    def logger(msg):
        print msg

    tnc = TncTrainer()
    tnc.train(net, inp, trg, logger)
