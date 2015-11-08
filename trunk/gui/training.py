from enthought.traits.api import *
from enthought.traits.ui.api import *
from multiprocessing import cpu_count
from redirfile import Redirector
import time


class Trainer(HasTraits):
    name = Str
    stopped = Any #Bool(True)

class TncTrainer(Trainer):
    name = Str('tnc')
    maxfun = Int(0)
    nproc = Int(cpu_count())
    messages = Int(1)

    def callback(self, x):
        #self.parent.send(self.stopped)
        #stopped = self.child.recv()
        if self.stopped.value:
            self.net.weights[:] = x
            if self.nproc > 1:
                self.net._clean_mp()  # This will raise AssertionError
                #self.net._mppool.terminate()
                #del self.net._mppool
            self.p.terminate()
            raise AssertionError

    def __repr__(self):
        return self.name

    def train(self, net, inp, trg, logger):
        self.net = net
        if not self.maxfun:
            self.maxfun = max(100, 10*len(net.weights))
        self.nproc = min(self.nproc, len(inp))  # should be in ffnet!
        r = Redirector(fd=2)  
        r.start() # Catch output
        t0 = time.time()
        try:
            #net.train_tnc(inp, trg, nproc=self.nproc, maxfun=self.maxfun, disp = self.messages, callback=self.callback)
            from multiprocessing import Process, Value
            self.stopped = Value('i', 0)
            p = Process(target=net.train_tnc, args=(inp, trg), kwargs={'nproc':self.nproc,
                                                                       'maxfun': self.maxfun,
                                                                       'disp': self.messages,
                                                                       'callback': self.callback})
            self.p = p
            p.start()
            p.join()
            #time.sleep(0.1)  # Wait a while for ui to be updated (it may rely on train_algorithm values)
            reason = 'Training finished normally.'
        except AssertionError:
            reason = 'Training stopped by user.'
        except:
            import traceback
            reason = traceback.format_exc()
        t1 = time.time()
        self.stopped = True
        output = r.stop() # Get catched output
        logger(output)
        logger(reason)
        logger('Execution time: %3.3f seconds' %(t1-t0))

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
