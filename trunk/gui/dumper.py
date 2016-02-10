#-*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

## from traits.etsconfig.api import ETSConfig
## ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *
import pyface.api as pyface
from ffnet import *
from messages import display_error
import numpy as np
import os


class Dumper(HasTraits):
    training_data_only = Bool(False)
    validation_data_only = Bool(False)
    normalized_data = Bool(False)
    input = Button
    target = Button
    output = Button
    output_derivatives = Button

    def _training_data_only_changed(self, new):
        if new:
            self.validation_data_only = False

    def _validation_data_only_changed(self, new):
        if new:
            self.training_data_only = False

    def dump(self, out, sufix):
        wildcard = 'Text file (*.txt)|*.txt'
        outfile = os.path.splitext(self.app.network.filename)[0] + '-' + sufix + '.txt'
        dialog = pyface.FileDialog(parent=None,
                                   title='Save as',
                                   action='save as',
                                   wildcard=wildcard,
                                   default_path=outfile
                                   )
        if dialog.open() == pyface.OK:  # path is given
            path = dialog.path
            try:
                np.savetxt(path, out, newline = os.linesep)
                self.app.logs.logger.info('%s saved to file: %s' %(sufix.capitalize().replace('-', ' '), path))
            except:
                display_error("Error when saving data!")
                return

    def _output_fired(self):
        net = self.app.net
        data = self.app.data
        out = net.call(data.input)
        sufix = 'output'
        if self.app.mode == 'train':
            if self.training_data_only:
                out = out[~data.vmask]
                sufix = 'training-' + sufix
            if self.validation_data_only:
                out = out[data.vmask]
                sufix = 'validation-' + sufix
        if self.normalized_data:
            out = ffnetmodule._normarray(out, net.eno)
            sufix = 'normalized-' + sufix
        self.dump(out, sufix)

    def _output_derivatives_fired(self):
        net = self.app.net
        data = self.app.data
        out = net.derivative(data.input)
        s = out.shape
        out = out.reshape((s[0], s[1]*s[2]))
        sufix = 'output-derivatives'
        if self.app.mode == 'train':
            if self.training_data_only:
                out = out[~data.vmask]
                sufix = 'training-' + sufix
            if self.validation_data_only:
                out = out[data.vmask]
                sufix = 'validation-' + sufix
        if self.normalized_data:
            out = out/net.ded.flatten()
            sufix = 'normalized-' + sufix
        self.dump(out, sufix)

    def _input_fired(self):
        net = self.app.net
        data = self.app.data
        out = data.input
        sufix = 'input'
        if self.app.mode == 'train':
            if self.training_data_only:
                out = out[~data.vmask]
                sufix = 'training-' + sufix
            if self.validation_data_only:
                out = out[data.vmask]
                sufix = 'validation-' + sufix
        if self.normalized_data:
            out = ffnetmodule._normarray(out, net.eni)
            sufix = 'normalized-' + sufix
        self.dump(out, sufix)

    def _target_fired(self):
        net = self.app.net
        data = self.app.data
        out = data.target
        sufix = 'target'
        if self.app.mode == 'train':
            if self.training_data_only:
                out = out[~data.vmask]
                sufix = 'training-' + sufix
            if self.validation_data_only:
                out = out[data.vmask]
                sufix = 'validation-' + sufix
        if self.normalized_data:
            out = ffnetmodule._normarray(out, net.eno)
            sufix = 'normalized-' + sufix
        self.dump(out, sufix)

    traits_view = View(
                       UItem('output'),
                       UItem('output_derivatives'),
                       UItem('input'),
                       UItem('target', visible_when="object.app.mode in ['train', 'test'] and object.app.data.status==2"),
                       Group(Item('training_data_only', visible_when="object.app.mode == 'train'"),
                             Item('validation_data_only', visible_when="object.app.mode == 'train'"),
                             Item('normalized_data')),
                       resizable = True,
                       width = 0.15,
                       #buttons = ['OK', 'Cancel'],
                       title = 'Dumping data...')
