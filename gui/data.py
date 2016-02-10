#-*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *
from loadtxt import LoadTxt
from messages import display_error
import numpy as np


class TrainingDataHandler(Handler):
    def close(self, info, is_ok):
        if is_ok:
            status = info.object.load()
            return status
        else:
            return True

class TrainingData(HasTraits):
    app = None
    input_loader = Instance(LoadTxt, ())
    target_loader = Instance(LoadTxt, ())
    input = DelegatesTo('input_loader', prefix='data')
    target = DelegatesTo('target_loader', prefix='data')
    input_n = CArray
    target_n = CArray
    vmask = CArray(dtype=np.bool)
    input_t = Property(CArray)
    target_t = Property(CArray)
    input_v = Property(CArray)
    target_v = Property(CArray)
    input_t_n = Property(CArray)
    target_t_n = Property(CArray)
    input_v_n = Property(CArray)
    target_v_n = Property(CArray)
    validation_patterns = Range(0, 50, 10)
    validation_type = Enum('random', 'last')
    normalize = Bool(True)
    status = Int(0)  # 1 - input loaded, 2 - input and target loaded
    status_info = Str('No data loaded.')

    def _get_input_t(self):
        return self.input[~self.vmask]

    def _get_input_v(self):
        return self.input[self.vmask]

    def _get_target_t(self):
        return self.target[~self.vmask]

    def _get_target_v(self):
        return self.target[self.vmask]

    def _get_input_t_n(self):
        return self.input_n[~self.vmask]

    def _get_input_v_n(self):
        return self.input_n[self.vmask]

    def _get_target_t_n(self):
        return self.target_n[~self.vmask]

    def _get_target_v_n(self):
        return self.target_n[self.vmask]

    #def clear(self):
        #self.input_loader = LoadTxt()
        #self.target_loader = LoadTxt()

    def load(self):
        inp0 = self.input
        trg0 = self.target
        if self.app.mode in ['train', 'test']:
            inp = self.input_loader.load(errmsg='Error occured during reading input file!')
            if not len(inp):
                return False
            trg = self.target_loader.load(errmsg='Error occured during reading target file!')
            if not len(trg):
                return False
            test1 = self.test_input()
            if not test1:
                return False
            test2 = self.test_target()
            if not test2:
                return False
            test3 = self.test_input_target()
            if not test3:
                return False
            if inp.shape == inp0.shape and trg.shape == trg0.shape:
                if np.allclose(inp - inp0, 0) and np.allclose(trg-trg0, 0):  # nothing new is loaded
                    return True
            self._set_status()
            if self.app.mode == 'train':
                self._set_validation_mask()
                self._normalize_data()
            return True
        else:
            inp = self.input_loader.load(errmsg='Error occured during reading input file!')
            if not len(inp):
                return False
            test1 = self.test_input()
            if not test1:
                return False
            if inp.shape == inp0.shape:
                if np.allclose(inp - inp0, 0):  # nothing new is loaded
                    return True
            self._set_status()
            return True
        return False

    def test_input(self):
        inp = self.input
        net = self.app.network.net
        if net is not None and len(inp):
            n1, n2 = inp.shape[1], len(net.inno)
            if n1 != n2:
                msg = "Network has %i inputs but input data has %i columns!" %(n2, n1)
                display_error(msg)
                return False
        return True

    def test_target(self):
        trg = self.target
        net = self.app.network.net
        if net is not None and len(trg):
            n1, n2 = trg.shape[1], len(net.outno)
            if n1 != n2:
                msg = "Network has %i targets but target data has %i columns!" %(n2, n1)
                display_error(msg)
                return False
        return True

    def test_input_target(self):
        inp = self.input
        trg = self.target
        #if not len(inp):
            #display_error("Set input data first!")
            #return False
        if len(inp) != len(trg):
            display_error("Training data is not aligned. "
                          "Input patterns: %i, Target patterns: %i" %(len(inp), len(trg)))
            return False
        return True

    #@on_trait_change('normalize')
    def _normalize_data(self):
        net = self.app.network.net
        if net and self.normalize:  #and self.status == 2:
            net.renormalize = self.normalize
            self.input_n, self.target_n = net._setnorm(self.input, self.target)
            self.normalize = False
            self.app.logs.logger.info('Normalization information has been calculated with current data.')

    #@on_trait_change('input, target')
    def _set_status(self):
        ni = len(self.input)
        nt = len(self.target)
        if ni and nt and ni == nt:
            self.status = 2
            self.status_info = '%i input and target patterns has been loaded (%i inputs, %i targets).'\
                                %(ni, self.input.shape[1], self.target.shape[1])
            #self._normalize_data()
            #self._set_validation_mask()

        elif ni and not nt:
            self.vmask = []
            self.input_n = []
            self.target_n = []
            self.status = 1
            self.status_info = '%i input patterns has been loaded (%i inputs).'\
                                %(ni, self.input.shape[1])
        else:
            self.vmask = []
            self.input_n = []
            self.target_n = []
            self.status = 0
            self.status_info = 'No usefull data loaded.'
        self.app.logs.logger.info(self.status_info)

    @on_trait_change('validation_patterns, validation_type')
    def _set_validation_mask(self):
        if self.status == 2:  # input and target are not empty and of the same length
            npat = len(self.input)
            self.vmask = ~np.ones(npat, np.bool)
            percent = self.validation_patterns
            npat_v = percent*npat/100
            type_ = self.validation_type
            if type_ == 'random':
                idx = np.random.choice(npat, npat_v)
                mask = np.in1d(np.arange(npat), idx)
                self.vmask = mask
            if type_ == 'last':
                mask = np.ones(npat, np.bool)
                mask[:npat-npat_v] = False
                self.vmask = mask
            if self.app:
                self.app.logs.logger.info('%i training patterns has been chosen for validation (%s)' %(npat_v, type_))

    #traits_view = View(Tabbed(UItem('input_loader', style='custom', label='Input data', dock='tab',
                              #height = 0.5),
                              #UItem('target_loader', style='custom', label='Target data',
                              #height = 0.5, visible_when='len(input)>0', dock='tab'),
                              #scrollable = True),
                       #Item('validation_patterns', visible_when='len(input)>0 and len(target)>0'),
                       #Item('validation_type', visible_when='len(input)>0 and len(target)>0'),
                       #Group(UItem('status_info', style='readonly', emphasized=True)),
                       ##Item('normalize', tooltip='Set normalization limits from current training data'),
                       #title = 'Loading data...',
                       #buttons = ['OK', 'Cancel'],
                       ##statusbar = [StatusItem(name = 'status_info')],
                       ##handler = TrainingDataHandler(),
                       #resizable = True,
                       #width = 0.3,
                       #height = 0.4)

    traits_view = View(Group(Item('input_loader',
                                   style='custom',
                                   label='Input file',),
                             Item('target_loader',
                                   style='custom',
                                   label='Target file'),
                             Group(Item('validation_patterns',
                                        label = 'Validation patterns [%]'),
                                   Item('validation_type'),
                                   Item('normalize')),
                             visible_when = 'object.app.mode == "train"'),
                       Group(Item('input_loader',
                                   style='custom',
                                   label='Input',),
                             Item('target_loader',
                                   style='custom',
                                   label='Target'),
                             visible_when = 'object.app.mode == "test"'),
                       Group(Item('input_loader',
                                   style='custom',
                                   label='Input',),
                             visible_when = 'object.app.mode == "recall"'),
                        buttons = ['OK', 'Cancel'],
                        handler = TrainingDataHandler(),
                        resizable = True,
                        width = 0.4)


if __name__ == "__main__":
    from ffnet import ffnet, mlgraph
    from logger import Logger
    class Network:
        net = ffnet(mlgraph((3,5,1)))
    class App(HasTraits):
        network = Network()
        logs = Logger()
        mode = 'train'
    #input = LoadInput(App())
    data = TrainingData(app=App())
    data.app.data = data
    data.configure_traits()
