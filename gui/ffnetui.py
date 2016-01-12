#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *

from network import Network
from data import TrainingData
from training import *
from shared import Shared
from logger import Logger
from animations import *
from plots.mplfigure import MPLPlotter
from actions import toolbar

class SettingsHandler(Handler):
    def close(self, info, is_ok):
        if is_ok:
            obj = info.object
            obj.data.input_loader.load()
            if obj.mode in ['train', 'test']:
                obj.data.target_loader.load()
            if obj._pmode != obj.mode or len(obj.plist) == 0:
                obj.arrange_plots()
            else:
                obj.selected.replot()
        #return True
        return Handler.close(self, info, is_ok)


class FFnetApp(HasTraits):
    network = Instance(Network)
    data = Instance(TrainingData)
    trainer = Instance(Trainer)
    shared = Instance(Shared)
    logs = Instance(Logger)
    plist = List([], value=MPLPlotter, transient=True) 
    selected = Instance(MPLPlotter, transient=True)  # Cannot be pickled when animation runs
    shell = PythonValue(Dict)
    mode = Enum('train', 'test', 'recall')
    algorithm = Enum('tnc', 'bfgs', 'cg')
    running = DelegatesTo('trainer')
    net = DelegatesTo('network')
    data_status = DelegatesTo('data',  prefix='status')

    def __init__(self, **traits):
        super(FFnetApp, self).__init__(**traits)
        self.network = Network(app = self)
        self.data = TrainingData(app = self)
        self.trainer = TncTrainer(app = self) # default trainer
        self.shared = Shared()
        self.logs = Logger()
        from ffnet import version
        self.logs.logger.info('Welcome! You are using ffnet-%s.' %version)
        self.shell = {'app':self}

    def new(self):
        net = self.network.create()
        if net is not None:
            self.mode = 'train'
            self.settings()

    def load(self):
        net = self.network.load()
        if net is not None:
            self.mode = 'recall'
            self.settings()

    def save_as(self):
        self.network.save_as()

    def export(self):
        raise NotImplementedError

    def settings(self):
        if self.net:
            self._pmode = self.mode
            self.edit_traits(view='settings_view', kind='modal')
            #if mode != self.mode or len(self.plist) == 0:
                #self.arrange_plots()
            #else:
                #self.selected.replot()

    def train_start(self):
        self.logs.logger.info('Training network: %s' %self.network.filename)
        self.trainer.train()

    def train_stop(self):
        self.trainer.running = False

    def reset(self):
        if self.net:
            self.net.randomweights()
            self.logs.logger.info('Weights has been randomized!')
        self.shared.populate() 
        self.selected.replot()

    def add_plot(self, cls):
        if any(isinstance(p, cls) for p in self.plist):  # plot is just opened
            for p in self.plist:
                if isinstance(p, cls):
                    if self.selected == p:
                        self.selected.replot()
                    else:
                        self.selected = p  # will be replotted automatically
                    break
        else:
            p = cls(app = self, interval=250)
            self.plist = self.plist + [p]
            self.selected = p

    def arrange_plots(self):
        self.plist = []
        if self.mode == 'train':
            plots = [ErrorAnimation, TOAnimation, IOAnimation, GraphAnimation]
        elif self.mode == 'test':
            plots = [TOAnimation, GraphAnimation]
        else:
            plots = [GraphAnimation]
        for p in plots:
            self.add_plot(p)
        self.selected = self.plist[0]

    def _algorithm_changed(self, new):
        if new == 'tnc':
            self.trainer = TncTrainer(app=self)
        if new == 'cg':
            self.trainer = CgTrainer(app=self)
        if new == 'bfgs':
            self.trainer = BfgsTrainer(app=self)

    def _selected_changed(self, old, new):
        if self.trainer.running:
            try:
                old.stop()  # Assume we have animation
            except:
                pass  # But simple plot can be also
            try:
                new.start()  # Assume we have animation
            except:
                new.replot()  # But simple plot can be also
        else:
            new.replot()

    traits_view = View(VSplit(Item('plist',
                            style='custom',
                            show_label=False,
                            height = 0.75,
                            editor=ListEditor(use_notebook=True,
                                              deletable=False,
                                              dock_style='tab',
                                              selected='selected',
                                              view = 'figure_view',
                                              page_name = '.name')),
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
                                     #show_labels = False
                                    )
                              ),
                             #),
                       title = 'ffnet - neural network trainer',
                       width = 0.6,
                       height = 0.8,
                       resizable = True,
                       #menubar = menubar,
                       toolbar = toolbar,
                       #statusbar = [StatusItem(name = '_progress', width=200)]
                       )

    settings_view = View(Item('mode', emphasized=True),
                         '_',
                         Group(Item('object.data.input_loader',
                                     style='custom',
                                     label='Input file',),
                                 Item('object.data.target_loader',
                                     style='custom',
                                     label='Target file'),
                                 Item('object.data.validation_patterns',
                                     label = 'Validation patterns [%]'),
                                 Item('object.data.validation_type'),
                                 Item('object.data.normalize'),
                                 visible_when = 'mode == "train"'),
                         Group(Item('object.data.input_loader',
                                     style='custom',
                                     label='Input',),
                                 Item('object.data.target_loader',
                                     style='custom',
                                     label='Target'),
                                 visible_when = 'mode == "test"'),
                         Group(Item('object.data.input_loader',
                                     style='custom',
                                     label='Input',),
                                 visible_when = 'mode == "recall"'),
                         '_',
                         Group(Item('algorithm', label = 'Training algorithm'), 
                                 UItem('object.trainer', style='custom'),
                                 visible_when='mode == "train"'),
                         buttons = ['OK', 'Cancel'],
                         handler = SettingsHandler(),
                         title = 'Settings...',
                         resizable = True,
                         width = 0.5)

    training_view = View(UItem('stop_training'),
                         title = 'Training network...',
                         width = 0.25)


def main():
    app = FFnetApp()
    app.configure_traits()

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
    app.data.input_loader.load()
    app.data.target_loader.filename = 'data/black-scholes-target.dat'
    app.data.target_loader.load()
    app.arrange_plots()
    # Run
    app.configure_traits()

if __name__=="__main__":
    import multiprocessing as mp
    mp.freeze_support()
    main()
    #test()
