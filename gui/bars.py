from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.pyface.image_resource import ImageResource

# Actions
new_network_action = Action(
    name   = 'New...', 
    action = '_new',
    image  = ImageResource( 'blue_ball'))

load_network_action = Action(
    name   = 'Load...', 
    action = '_load',
    image  = ImageResource( 'blue_ball'))

save_as_network_action = Action(
    name   = 'Save...', 
    action = '_save_as',
    image  = ImageResource( 'blue_ball'),
    enabled_when = 'object.netlist')

remove_network_action = Action(
    name   = 'Remove', 
    action = '_remove',
    image  = ImageResource( 'blue_ball'),
    enabled_when = 'object.netlist')

export_network_action = Action(
    name   = 'Export', 
    action = '_export',
    image  = ImageResource( 'blue_ball'),
    enabled_when = 'False')

input_data_action = Action(
    name   = 'Input', 
    action = '_load_input_data',
    image  = ImageResource( 'blue_ball'),
    enabled_when = 'netlist')

target_data_action = Action(
    name   = 'Target', 
    action = '_load_target_data',
    image  = ImageResource( 'blue_ball'),
    enabled_when = 'object.netlist and object.input_data.filename')

training_settings_action = Action(
    name   = 'Settings', 
    action = '_train_settings',
    image  = ImageResource( 'blue_ball'),
    enabled_when = 'object.input_data and object.target_data')

train_action = Action(
    name   = 'Train!', 
    action = '_train',
    image  = ImageResource( 'blue_ball'),
    enabled_when = 'netlist and not object.train_algorithm.running.value')

train_stop_action = Action(
    name   = 'Stop!', 
    action = '_train_stop',
    image  = ImageResource( 'blue_ball'),
    enabled_when = 'netlist and object.train_algorithm.running.value')


# Groups of actions
network_actions = Separator(
    new_network_action,
    load_network_action,
    save_as_network_action,
    remove_network_action,
    export_network_action)

data_actions = Separator(
    input_data_action,
    target_data_action)

train_actions = Separator(
    training_settings_action,
    train_action,
    train_stop_action)

# File menu
file_menu = Menu(network_actions,
                 data_actions,
                 name = 'File')
train_menu = Menu(train_actions,
                  name = 'Train')

menubar = MenuBar(file_menu, train_menu)
toolbar = ToolBar(network_actions,
                  data_actions,
                  train_actions)
