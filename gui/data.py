#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from enthought.traits.api import *
from enthought.traits.ui.api import *
import pyface.api as pyface
from loadtxt import LoadTxt
from messages import display_error, display_confirm
import numpy as np


class LoadInput(LoadTxt):
    def __init__(self, app=None, **traits):
        super(LoadInput, self).__init__(**traits)
        self.app = app
        self.title = ''

    def validate(self, data):
        if not len(data):
            display_error("No data loaded! Empty file?")
            return data
        if not self.test_network(data):
            return []
        msg = "Loaded %i input patterns from file: %s" %(data.shape[0],
                                                         self.filename)
        self.app.logs.logger.info(msg)
        # Possibly target has been set earlier so check it
        trg = self.app.data.target
        if len(trg):
            if not self.app.data.target_loader.test_input(trg):
                self.app.data.target = []
        return data

    def test_network(self, data):
        inp = data
        net = self.app.network.net
        if net is not None and len(inp):
            n1, n2 = inp.shape[1], len(net.inno)
            if n1 != n2:
                msg = "Network has %i inputs but input data has %i columns!\n\n" %(n2, n1)
                msg += "Proceed?"
                return display_confirm(msg)
        return True


class LoadTarget(LoadTxt):
    def __init__(self, app=None, **traits):
        super(LoadTarget, self).__init__(**traits)
        self.app = app
        self.title = ''

    def validate(self, data):
        if not len(data):
            display_error("No data loaded! Empty file?")
            return data
        if not self.test_input(data):
            return []
        if not self.test_network(data):
            return []
        msg = "Loaded %i target patterns from file: %s" %(data.shape[0],
                                                         self.filename)
        self.app.logs.logger.info(msg)
        return data

    def test_network(self, data):
        trg = data
        net = self.app.network.net
        if net is not None and len(trg):
            n1, n2 = trg.shape[1], len(net.outno)
            if n1 != n2:
                msg = "Network has %i targets but target data has %i columns!\n\n" %(n2, n1)
                msg += "Proceed?"
                return display_confirm(msg)
        return True

    def test_input(self, data):
        inp = self.app.data.input_loader.data
        trg = data
        if not len(inp):
            display_error("Set input data first!")
            return False
        if len(inp) != len(trg):
            display_error("Training data is not aligned. "
                          "Input patterns: %i, target_patterns: %i" %(len(inp), len(trg)))
            return False
        return True


class TrainingDataHandler(Handler):
    def close(self, info, is_ok):
        if is_ok:
            status = info.object.load()
            return status
        else:
            return True


class TrainingData(HasTraits):
    input_loader = Instance(LoadInput, ())
    target_loader = Instance(LoadTarget, ())
    input = DelegatesTo('input_loader', prefix='data')
    target = DelegatesTo('target_loader', prefix='data')
    vmask = CArray(dtype=np.bool)
    input_t = Property(CArray)
    target_t = Property(CArray)
    input_v = Property(CArray)
    target_v = Property(CArray)
    validation_patterns = Range(0, 50, 10)
    validation_type = Enum('random', 'last')
    status = Int(0)  # 1 - input loaded, 2 - input and target loaded
    status_info = Str('No data loaded.')

    def __init__(self, app = None, **traits):
        super(TrainingData, self).__init__(**traits)
        # App is not a trait?
        self.input_loader.app = app
        self.target_loader.app = app
        self.app = app

    def load(self):
        inp = self.input_loader.load()
        trg = self.target_loader.load()
        return True

    def _get_input_t(self):
        return self.input[~self.vmask]

    def _get_input_v(self):
        return self.input[self.vmask]

    def _get_target_t(self):
        return self.target[~self.vmask]

    def _get_target_v(self):
        return self.target[self.vmask]

    @on_trait_change('input', 'target')
    def _set_status(self):
        ni = len(self.input)
        nt = len(self.target)
        if ni and nt and ni == nt:
            self.status = 2
            self.status_info = '%i input and target patterns are loaded (%i inputs, %i targets).'\
                                %(ni, self.input.shape[1], self.target.shape[1])
        elif ni and not nt:
            self.status = 1
            self.status_info = '%i input patterns are loaded(%i inputs).'\
                                %(ni, self.input.shape[1])
        else:
            self.status = 0
            status_info = 'No data loaded.'

    @on_trait_change('validation_patterns', 'validation_type', 'input', 'target')
    def _set_validation_mask(self):
        self._set_status()
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
            self.app.logs.logger.info('%i training patterns chosen for validation (%s)' %(npat_v, type_))

    traits_view = View(Tabbed(UItem('input_loader', style='custom', label='Input data', dock='tab',
                              height = 0.5),
                              UItem('target_loader', style='custom', label='Target data',
                              height = 0.5, visible_when='len(input)>0', dock='tab'),
                              scrollable = True),
                       Item('validation_patterns', visible_when='len(input)>0 and len(target)>0'),
                       Item('validation_type', visible_when='len(input)>0 and len(target)>0'),
                       Group(UItem('status_info', style='readonly', emphasized=True)),
                       #Item('normalize', tooltip='Set normalization limits from current training data'),
                       title = 'Loading data...',
                       buttons = ['OK', 'Cancel'],
                       #statusbar = [StatusItem(name = 'status_info')],
                       #handler = TrainingDataHandler(),
                       resizable = True,
                       width = 0.3,
                       height = 0.4)


if __name__ == "__main__":
    from ffnet import ffnet, mlgraph
    from logger import Logger
    class Network:
        net = ffnet(mlgraph((3,5,1)))
    class App:
        network = Network()
        logs = Logger()
    #input = LoadInput(App())
    data = TrainingData(App())
    data.app.data = data
    data.configure_traits()
