#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from enthought.traits.api import *
from enthought.traits.ui.api import *
from loadtxt import LoadTxt
from network import Network
from training import TncTrainer
import thread
import sys


class Trainer(HasTraits):
    netlist = List(values=Instance(Network))
    network = Enum(values='netlist')
    new = Button
    remove = Button
    save_as = Button
    load = Button
    export = Button
    #
    input_data = Instance(LoadTxt, ())
    target_data = Instance(LoadTxt, ())
    trainers = List([TncTrainer()])
    train_algorithm = Enum(values='trainers')
    train_settings = Button
    train = Button
    stop_training = Button
    output = Code
    output_selected_line = Int
    # values={}

    def log(self, message):
        self.output += message + '\n'

    def _output_changed(self):
        self.output_selected_line = self.output.count('\n')

    def _new_fired(self):
        n = Network()
        n.edit_traits(kind='modal')
        if n.net is not None:
            self.netlist.append(n)
            self.network = n
            self.log('Network created: %s' %n.name)

    def _remove_fired(self):
        if len(self.netlist) != 0:
            idx = self.netlist.index(self.network)
            name = self.network.name
            del self.netlist[idx]
            self.log('Network removed (from memory): %s' %name)

    def _save_as_fired(self):
        oldname = self.network.name
        success = self.network.save_as() # Open dialog
        if success:
            # Hack for changing name in the Enum list
            n = self.network
            self.netlist.append(Network())
            self.network = self.netlist[-1]
            self.netlist = self.netlist[:-1]
            self.network = n
            # Log
            newname = self.network.name
            if newname == oldname:
                self.log('Network saved: %s' %oldname)
            else:
                self.log('Network %s saved as: %s' %(oldname, newname))

    def _load_fired(self):
        n = Network()
        n.load()  # Open dialog
        if n.net is not None:
            self.netlist.append(n)
            self.network = n
            self.log('Network loaded: %s' %n.name)
    
    def _export_fired(self):
        raise NotImplementedError
    
    def _train_settings_fired(self):
        self.train_algorithm.edit_traits(kind='modal')
    
    def _train_fired(self):
        self.log('Training network: %s' %self.network.name)
        inp = self.input_data.load()
        trg = self.target_data.load()
        # self.train_algorithm.train(self.network.net, inp, trg, self.log)
        thread.start_new_thread(self.train_algorithm.train, (self.network.net, inp, trg, self.log))

    def _stop_training_fired(self):
        self.train_algorithm.stopped = True  # will raise exception


    traits_view = View(VSplit(Tabbed(
                              VGroup(Group(UItem('network', emphasized=True, enabled_when='netlist')),
                                     UItem('new'),
                                     UItem('load'),
                                     UItem('save_as', enabled_when='netlist'),
                                     UItem('export', enabled_when = 'False'),
                                     UItem('remove', enabled_when='netlist'),
                                     label = 'Network',
                                     show_border=True,
                                     ),
                              VGroup(Group(UItem('network', emphasized=True, enabled_when='netlist')),
                                     Item('input_data', style='custom'),
                                     Item('target_data', style='custom'),
                                     HGroup(
                                            Item('train_algorithm'),
                                            UItem('train_settings', label='Settings'),
                                            #label = 'Train algorithm'
                                            ),
                                     UItem('train', emphasized=True, enabled_when='netlist and object.train_algorithm.stopped'),
                                     UItem('stop_training', emphasized=True, enabled_when='netlist and not object.train_algorithm.stopped'),
                                     label = 'Training',
                                     show_border = True,
                                     )),
                              Tabbed(
                                     Item('output',
                                          style  = 'readonly',
                                          #editor = c,
                                          editor = CodeEditor(show_line_numbers = False,
                                                              selected_color    = 0xFFFFFF,
                                                              selected_line = 'output_selected_line',
                                                              auto_scroll = True),
                                          dock   = 'tab',
                                          export = 'DockWindowShell'
                                          ),
                                    #Item( 'values',
                                        #id     = 'values_1',
                                        #label  = 'Shell',
                                        #editor = ShellEditor( share = True ),
                                        #dock   = 'tab',
                                        #export = 'DockWindowShell'
                                    #),
                                    #Item( 'values',
                                        #id     = 'values_2',
                                        #editor = ValueEditor(),
                                        #dock   = 'tab',
                                        #export = 'DockWindowShell'
                                    #),
                                    show_labels = False
                                   ),
                             ),
                       title = 'ffnet - neural network trainer',
                       width=0.4,
                       height=0.5,
                       resizable = True,
                       )


t = Trainer()
t.configure_traits()