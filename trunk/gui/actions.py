#-*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

from traits.api import *
from traitsui.api import *
from pyface.image_resource import ImageResource

# Actions
new_network_action = Action(
    name   = 'New...', 
    action = 'new',
    image  = ImageResource('document-new'),
    enabled_when = 'not object.trainer.running',
    tooltip = 'Create new network'
    )

load_network_action = Action(
    name   = 'Load...', 
    action = 'load',
    image  = ImageResource('document-open'),
    enabled_when = 'not running',
    tooltip = 'Load previously saved network'
    )

save_as_network_action = Action(
    name   = 'Save...', 
    action = 'save_as',
    image  = ImageResource('document-save-as'),
    enabled_when = 'net and not running',
    tooltip = 'Save network for later load')

export_network_action = Action(
    name   = 'Export', 
    action = 'export',
    image  = ImageResource('text-x-fortran'),
    enabled_when = 'net and not running',
    tooltip = 'Export network to Fortran source file')

dump_action = Action(
    name   = 'Dump', 
    action = 'dump',
    image  = ImageResource('text-x-generic'),
    enabled_when = 'net and data.status>0 and not running',
    tooltip = 'Dump output (or input, or target) data to text file')

settings_action = Action(
    name   = 'Setup', 
    action = 'settings',
    image  = ImageResource('preferences-system'),
    enabled_when = 'net and not running',
    tooltip = 'Settings')

train_start_action = Action(
    name   = 'Train!', 
    action = 'train_start',
    image  = ImageResource('go-next'),
    enabled_when = 'net and mode == "train" and data_status == 2 and not running',
    tooltip = 'Start training')

train_stop_action = Action(
    name   = 'Stop!', 
    action = 'train_stop',
    image  = ImageResource('media-record'),
    enabled_when = 'running',
    tooltip = 'Stop training')

train_reset_action = Action(
    name   = 'Reset', 
    action = 'reset',
    image  = ImageResource('edit-clear'),
    enabled_when = 'net and mode == "train" and data_status == 2 and not running',
    tooltip = 'Reset weights and training results')

about_action = Action(
    name   = 'About', 
    action = 'about',
    image  = ImageResource('help-browser'),
    tooltip = 'Show about dialog')

donate_action = Action(
    name   = 'Donate', 
    action = 'donate',
    image  = ImageResource('face-smile.png'),
    tooltip = 'Please, donate ffnet/ffnetui development')

cite_action = Action(
    name   = 'Cite', 
    action = 'cite',
    image  = ImageResource('accessories-text-editor.png'),
    tooltip = 'Please, cite ffnet/ffnetui related works')

# Groups of actions
network_actions = ActionGroup(
    new_network_action,
    load_network_action,
    save_as_network_action,
    export_network_action,
    dump_action
    )

train_actions = ActionGroup(
    settings_action,
    train_start_action,
    train_stop_action,
    train_reset_action,
    )

help_actions = ActionGroup(
    about_action,
    cite_action,
    donate_action
    )

# File menu
file_menu = Menu(network_actions,
                 name = 'File')
train_menu = Menu(train_actions,
                  name = 'Train')
help_menu = Menu(help_actions,
                 name = 'Help')

menubar = MenuBar(file_menu, train_menu, help_menu)
toolbar = ToolBar(network_actions,
                  train_actions,
                  #help_actions,
                  image_size=(22, 22))
