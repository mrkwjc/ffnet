#-*- coding: utf-8 -*-
## from traits.etsconfig.api import ETSConfig
## ETSConfig.toolkit = 'qt4'

from traits.api import *
from traitsui.api import *
from traitsui.ui_editors.array_view_editor import ArrayViewEditor
import pyface.api as pyface
import matplotlib
import numpy as np
import networkx as nx
import os

from ffnet_import import *
from messages import display_error


class Dumper(HasTraits):
    training_data_only = Bool(False)
    validation_data_only = Bool(False)
    normalized_data = Bool(False)
    input = Button
    target = Button
    output = Button
    output_derivatives = Button
    app = Any
    net = DelegatesTo('app')
    data = DelegatesTo('app')

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
                self.app.logs.logger.info('%s saved to file: %s' %(sufix.capitalize().replace('-', ''), path))
            except:
                display_error("Error when saving data!")
                return

    def _output_fired(self):
        out = self.net.call(self.data.input)
        sufix = 'output'
        if self.app.mode == 'train':
            if self.training_data_only:
                out = out[~self.data.vmask]
                sufix = 'training-' + sufix
            if self.validation_data_only:
                out = out[self.data.vmask]
                sufix = 'validation-' + sufix
        if self.normalized_data:
            out = ffnetmodule._normarray(out, self.net.eno)
            sufix = 'normalized-' + sufix
        self.dump(out, sufix)

    def _output_derivatives_fired(self):
        out = self.net.derivative(inp)
        s = out.shape
        out = out.reshape((s[0], s[1]*s[2]))
        sufix = 'output-derivatives'
        if self.app.mode == 'train':
            if self.training_data_only:
                out = out[~self.data.vmask]
                sufix = 'training-' + sufix
            if self.validation_data_only:
                out = out[self.data.vmask]
                sufix = 'validation-' + sufix
        if self.normalized_data:
            out = out/self.net.ded.flatten()
            sufix = 'normalized-' + sufix
        self.dump(out, sufix)

    def _input_fired(self):
        out = self.data.input
        sufix = 'input'
        if self.app.mode == 'train':
            if self.training_data_only:
                out = out[~self.data.vmask]
                sufix = 'training-' + sufix
            if self.validation_data_only:
                out = out[self.data.vmask]
                sufix = 'validation-' + sufix
        if self.normalized_data:
            out = ffnetmodule._normarray(out, self.net.eni)
            sufix = 'normalized-' + sufix
        self.dump(out, sufix)

    def _target_fired(self):
        out = self.data.target
        sufix = 'target'
        if self.app.mode == 'train':
            if self.training_data_only:
                out = out[~self.data.vmask]
                sufix = 'training-' + sufix
            if self.validation_data_only:
                out = out[self.data.vmask]
                sufix = 'validation-' + sufix
        if self.normalized_data:
            out = ffnetmodule._normarray(out, self.net.eno)
            sufix = 'normalized-' + sufix
        self.dump(out, sufix)

    traits_view = View(Group(Item('training_data_only', visible_when="object.app.mode == 'train'"),
                             Item('validation_data_only', visible_when="object.app.mode == 'train'"),
                             Item('normalized_data')),
                       UItem('output'),
                       UItem('output_derivatives'),
                       UItem('input'),
                       UItem('target', visible_when="object.app.mode in ['train', 'test'] and object.data.status==2"),
                       resizable = True,
                       width = 0.15,
                       buttons = ['OK', 'Cancel'],
                       title = 'Dumping data...')
