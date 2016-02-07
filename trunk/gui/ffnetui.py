#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *
from pyface.image_resource import ImageResource

from network import Network
from data import TrainingData
from dumper import Dumper
from training import *
from shared import Shared
from logger import Logger
from animations import *
from plots.mplfigure import MPLPlots
from actions import toolbar
from messages import display_confirm


class View(View):
    icon = ImageResource('ffnetui128x128.ico')


class SettingsHandler(Handler):
    def close(self, info, is_ok):
        if is_ok:
            obj = info.object
            obj.logs.logger.info('Current mode is: "%s"' %obj.mode)
            status = obj.data.load()
            if not status:
                return False
            if obj._pmode != obj.mode or len(obj.plots.plots) == 0:
                obj._arrange_plots()
            else:
                obj.plots.selected.replot()
        return True
        #return Handler.close(self, info, is_ok)


class FFnetAppHandler(Handler):
    def close(self, info, is_ok):
        if is_ok:
            obj = info.object
            ok = display_confirm("Exiting. Are you sure?")
            if not ok:
                return False
            if obj.trainer.running:
                obj.train_stop()
                obj.trainer.training_thread.join() # Wait for finishing
        return True


class FFnetApp(HasTraits):
    network = Instance(Network)
    data = Instance(TrainingData)
    training_data = Instance(TrainingData)
    testing_data = Instance(TrainingData)
    recall_data = Instance(TrainingData)
    dumper = Instance(Dumper)
    trainer = Instance(Trainer)
    shared = Instance(Shared)
    logs = Instance(Logger)
    plots = Instance(MPLPlots, transient=True)
    shell = PythonValue(Dict)
    mode = Enum('train', 'test', 'recall')
    algorithm = Enum('tnc') #, 'bfgs', 'cg')
    running = DelegatesTo('trainer')
    net = DelegatesTo('network')
    data_status = DelegatesTo('data',  prefix='status')
    selected = DelegatesTo('plots')

    def __init__(self, **traits):
        super(FFnetApp, self).__init__(**traits)
        self.network = Network(app = self)
        self.training_data = TrainingData(app = self)
        self.testing_data = TrainingData(app = self)
        self.recall_data = TrainingData(app = self)
        self.data = self.training_data  # by default
        self.dumper = Dumper(app=self)
        self.trainer = TncTrainer(app = self) # default trainer
        self.shared = Shared()
        self.logs = Logger()
        self.plots = MPLPlots()
        from ffnet import version
        self.logs.logger.info('Welcome! You are using ffnet-%s.' %version)
        self.shell = {'app':self}

    def new(self):
        net = self.network.create()
        if net is not None:
            self.mode = 'train'
            self.data.normalize = True
            self._new_net_setup()

    def load(self):
        net = self.network.load()
        if net is not None:
            self.mode = 'recall'
            self._new_net_setup()

    def save_as(self):
        self.network.save_as()

    def export(self):
        self.network.export()

    def dump(self):
        self.dumper.configure_traits(kind='modal')

    def settings(self):
        if self.net:
            self._pmode = self.mode
            self.edit_traits(view='settings_view', kind='livemodal')

    def train_start(self):
        self.logs.logger.info('Training network: %s' %self.network.filename)
        self.trainer.train()

    def train_stop(self):
        self.trainer.running = False

    def reset(self):
        if self.net:
            self.net.randomweights()
            self.logs.logger.info('Weights has been randomized!')
        self.clear()

    def about(self):
        from about import about
        about.open()

    def clear(self):
        self.shared.populate() 
        self.plots.selected.replot()

    def _arrange_plots(self):
        if self.mode == 'train':
            plots = [ErrorAnimation,
                     RegressionAnimation,
                     TOAnimation,
                     DOAnimation,
                     ITOAnimation,
                     DIOAnimation,
                     GraphAnimation]
        elif self.mode == 'test':
            plots = [RegressionPlot,
                     TOPlot,
                     DOAnimation,
                     ITOPlot,
                     DIOAnimation,
                     GraphAnimation]
        else:
            plots = [OPlot,
                     DOAnimation,
                     IOPlot,
                     DIOAnimation,
                     GraphAnimation]
        self.plots.classes = plots
        self.plots.selected.replot()

    def _new_net_setup(self):
        self.shared.populate()  # Clears all data from previous training
        data_status = False
        if self.data.status == 2:
            data_status = self.data.load()  # here we test data
        if not data_status:
            self.data.status = 0
            self.settings()
        else:
            self._arrange_plots()
            self.logs.logger.info('Using previously loaded data.')

    def _mode_changed(self):
        if self.mode  == 'train':
            self.data = self.training_data
        elif self.mode == 'test':
            self.data = self.testing_data
        else:
            self.data = self.recall_data

    def _algorithm_changed(self, new):
        if new == 'tnc':
            self.trainer = TncTrainer(app=self)
        if new == 'cg':
            self.trainer = CgTrainer(app=self)
        if new == 'bfgs':
            self.trainer = BfgsTrainer(app=self)

    def _selected_changed(self, old, new):
        new.app = self  # TODO: Plots should be initialized with 'app=self' ?

    traits_view = View(VSplit(UItem('plots', style = 'custom', height=0.75,
                                    visible_when='len(object.plots.plots) > 0 and '
                                                 '((mode in ["train", "test"] and data_status == 2) or '
                                                 '(mode in ["recall"] and data_status == 1))'),
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
                                    )
                              ),
                       handler = FFnetAppHandler(),
                       title = 'Feed-forward neural network',
                       width = 0.6,
                       height = 0.8,
                       resizable = True,
                       toolbar = toolbar,
                       #menubar = menubar,
                       #statusbar = [StatusItem(name = 'net_info', width=0.5),
                                    #StatusItem(name = 'data_info', width=0.5)]
                       )

    settings_view = View(Item('mode', emphasized=True),
                         '_',
                        Group(Item('object.data.input_loader',
                                   style='custom',
                                   label='Input file',),
                             Item('object.data.target_loader',
                                   style='custom',
                                   label='Target file'),
                             Group(Item('object.data.validation_patterns',
                                        label = 'Validation patterns [%]'),
                                   Item('object.data.validation_type'),
                                   Item('object.data.normalize')),
                             visible_when = 'mode == "train"'),
                       Group(Item('object.data.input_loader',
                                   style='custom',
                                   label='Input file',),
                             Item('object.data.target_loader',
                                   style='custom',
                                   label='Target file'),
                             visible_when = 'mode == "test"'),
                       Group(Item('object.data.input_loader',
                                   style='custom',
                                   label='Input file',),
                             visible_when = 'mode == "recall"'),
                         '_',
                         Group(Item('algorithm', label = 'Training algorithm'), 
                               UItem('object.trainer', style='custom'),
                               Item('object.trainer.best_weights'),
                               visible_when='mode == "train"'),
                         buttons = ['OK', 'Cancel'],
                         handler = SettingsHandler(),
                         title = 'Settings...',
                         resizable = True,
                         scrollable = True,
                         width = 0.4)



def main():
    app = FFnetApp()
    app.configure_traits()
    return app

def test():
    app = FFnetApp()
    # Add test network
    from ffnet import loadnet
    n = app.network
    path = 'data/testnet.net'
    n.net = loadnet(path)
    n.filename = path
    ## Add test data
    app.data.input_loader.filename = 'data/black-scholes-input.dat'
    app.data.target_loader.filename = 'data/black-scholes-target.dat'
    app.data.load()
    app.mode = 'train'
    app._arrange_plots()
    # Run
    app.configure_traits()
    return app

if __name__=="__main__":
    import multiprocessing as mp
    mp.freeze_support()
    #app = main()
    app = test()
