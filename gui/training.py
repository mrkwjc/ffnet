from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.traits.ui.ui_editors.array_view_editor import ArrayViewEditor
import numpy
from multiprocessing import cpu_count, active_children
import time
from redirfile import Redirector

class MomentumOptions(HasTraits):
    eta = Float
    momentum = Float


class TncOptions(HasTraits):
    maxfun = Int
    messages = Int


class TrainOptions(HasTraits):
    algorithm = Enum('tnc', 'momentum')
    tnc = Instance(TncOptions, ())
    momentum = Instance(MomentumOptions, ())
    options = Button
    
    traits_view = View(HGroup(UItem('algorithm'),
                              UItem('options')),
                       resizable= True)
    
    def _options_fired(self):
        eval('self.%s.edit_traits()' %self.algorithm)

#TrainOptions().configure_traits()

class Trainer(HasTraits):
    name = Str
    stop = Bool(False)

class TncTrainer(Trainer):
    name = Str('tnc')
    maxfun = Int(0)
    nproc = Int(cpu_count())
    messages = Int(1)
    stopped = Bool(True)

    def callback(self, x):
        if self.stopped:
            self.net.weights[:] = x
            if self.nproc > 1:
                self.net._clean_mp()  # This will raise AssertionError
                #self.net._mppool.terminate()
                #del self.net._mppool
            raise AssertionError

    def __repr__(self):
        return self.name

    def train(self, net, inp, trg, logger):
        self.net = net
        logger('Using TNC trainig algorithm...\n')
        if not self.maxfun:
            self.maxfun = max(100, 10*len(net.weights))
        self.nproc = min(self.nproc, len(inp))  # should be in ffnet!
        r = Redirector(fd=2)  
        r.start() # Catch output
        self.stopped = False
        t0 = time.time()
        try:
            net.train_tnc(inp, trg, nproc=self.nproc, maxfun=self.maxfun, disp = self.messages, callback=self.callback)
            reason = 'Training finished normally.'
        except AssertionError:
            reason = 'Training stopped.'
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
