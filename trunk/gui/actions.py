from traits.api import *
from traitsui.api import *
from pyface.image_resource import ImageResource

# Actions
new_network_action = Action(
    name   = 'New...', 
    action = '_new',
    image  = ImageResource('document-new'),
    enabled_when = 'not object.trainer.running'
    )

load_network_action = Action(
    name   = 'Load...', 
    action = '_load',
    image  = ImageResource('document-open'),
    enabled_when = 'not running'
    )

save_as_network_action = Action(
    name   = 'Save...', 
    action = '_save_as',
    image  = ImageResource('document-save-as'),
    enabled_when = 'net and not running')

export_network_action = Action(
    name   = 'Export', 
    action = '_export',
    image  = ImageResource('text-x-generic-template'),
    enabled_when = 'net and not running')

close_network_action = Action(
    name   = 'Close', 
    action = '_close',
    image  = ImageResource('process-stop'),
    enabled_when = 'net and not running')

load_data_action = Action(
    name   = 'Data', 
    action = '_load_data',
    image  = ImageResource('text-x-generic'),
    enabled_when = 'net and not running')

training_setup_action = Action(
    name   = 'Setup', 
    action = '_train_settings',
    image  = ImageResource('preferences-system'),
    enabled_when = 'net and data_status == 2 and not running')
    #enabled_when = 'net and  object.trg.shape[1] == len(object.net.outno) and ' + \
                   #'len(object.inp) == len(object.trg) and not running')

train_start_action = Action(
    name   = 'Train!', 
    action = '_train_start',
    image  = ImageResource('go-next'),
    enabled_when = 'net and data_status == 2 and not running')

train_stop_action = Action(
    name   = 'Stop!', 
    action = '_train_stop',
    image  = ImageResource('media-record'),
    enabled_when = 'running')

train_reset_action = Action(
    name   = 'Reset', 
    action = '_reset',
    image  = ImageResource('edit-clear'),
    enabled_when = 'net and data_status == 2 and not running')

plots_select_action = Action(
    name   = 'Plots',
    action = 'object.plots.plots_select',
    image  = ImageResource('matplotlib'),
    enabled_when = 'True')


# Groups of actions
network_actions = ActionGroup(
    new_network_action,
    load_network_action,
    save_as_network_action,
    export_network_action,
    close_network_action)

data_actions = ActionGroup(
    load_data_action)

train_actions = ActionGroup(
    training_setup_action,
    train_start_action,
    train_stop_action,
    train_reset_action,
    plots_select_action)

#plot_actions = ActionGroup(

# File menu
file_menu = Menu(network_actions,
                 data_actions,
                 name = 'File')
train_menu = Menu(train_actions,
                  name = 'Train')

menubar = MenuBar(file_menu, train_menu)
toolbar = ToolBar(network_actions,
                  data_actions,
                  train_actions,
                  image_size=(22, 22))
