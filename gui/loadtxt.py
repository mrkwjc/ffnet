# -*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.traits.ui.ui_editors.array_view_editor import ArrayViewEditor
import pyface.api as pyface
import numpy
from types import IntType


class SliceStr(BaseStr):
    """
    String from which a sequence of slices can be generated.
    Valid values are, eg.:  '1,2,3', '1:10:2', '1,2,5:7,10:20,30::2'
    """
    default_value = ':'
    
    def validate(self, object, name, value):
        value = super(SliceStr, self).validate(object, name, value)
        if value == '': return ':'
        items = value.split(',')
        for item in items:
            if item == '': self.error(object, name, value)
            #item.replace('-', ':')
            if item.count(':') > 2: self.error(object, name, value)
            item = item.split(':')
            for i in item:
                if i != '':
                    try:
                        val = eval(i)
                        if type(val) is IntType: pass
                        else: self.error(object, name, value)
                    except:
                        self.error(object, name, value)
        return value
    
    def info(self):
        return "string for slicing "


class LoadTxtHandler(Handler):
    def close(self, info, is_ok):
        if is_ok:
            data = info.object.load()
            return True if data is not None else False
        else:
            return True

class LoadTxt(HasTraits):
    """
    Class for loading text files into numpy arrays.
    Based on numpy.loadtxt
    """   
    filename = File
    skiprows = Int
    dtype = Enum(['float', 'int', 'str'])
    decimal = Enum(['.', ','])
    delimiter = Str
    columns = SliceStr
    rows = SliceStr
    comments = Str('#')
    converters = Dict(Int, Callable)
    data = CArray
    updated = Bool(False)  # ff new data was loaded
   
    def load(self):
        """
        Loads text file to numpy array
        Array is returned and saved to 'data' attribute.
        """
        try:
            file = self._openfile()
            data = numpy.loadtxt(file,
                                dtype = self.dtype,
                                comments = self.comments or None,
                                delimiter = self.delimiter or None,
                                converters = self.converters,
                                skiprows = self.skiprows,
                                ndmin = 2)
            self.data = self._sliced(data)
            self.updated = True
            return self.data
        except:
            import sys
            e = sys.exc_info()[1]
            pyface.error(None, "Network cannot be created!\n\n" + e.message)
            return None

    def _openfile(self):
        """
        Opens file and performs decimal mark check
        """
        file = open(self.filename, 'r')
        if self.dtype == 'float' and self.decimal == ',':  #we have to replace ',' with '.'
            string = file.read(); file.close()
            string = string.replace(',', '.')
            # now write string to virtual file
            import cStringIO; file2 = cStringIO.StringIO()
            file2.write(string); file2.seek(0)
            return file2
        return file
        
    def _sliced(self, data):
        """
        Slices 'data' (numpy array) with given strings
        """
        # slice rows
        sliced_data = []
        for item in self.rows.split(','): 
            sliced_data += [eval('data[' + item + ']')]
        data = numpy.vstack(sliced_data)
        
        # slice columns
        sliced_data = []
        for item in self.columns.split(','):  # slice columns
            sliced_data += [eval('data[:,' + item + ']').T]
        data = numpy.vstack(sliced_data).T
        
        return data

    ### VIEW STUFF
    show_options = Button
    show_options_status = Bool(False)
    options = Button
    preview = Button

    def _options_fired(self):
        #self.show_options_status = not self.show_options_status
        self.edit_traits(view = 'options_view') 

    def _show_options_fired(self):
        self.show_options_status = not self.show_options_status

    def _preview_fired(self):
        self.load()
        self.edit_traits(view = 'array_view') 

    traits_view = View(HGroup(UItem('filename', resizable=True, springy=True),
                              UItem('options'),
                              UItem('preview')),
                       #title = 'Loading text file...',
                       width = 0.4)

    options_view = View(Item('dtype',     label='Data type'),
                        Item('decimal',   label='Decimal'),
                        Item('delimiter', label='Delimiter'),
                        Item('columns',   label='Columns'),
                        Item('rows',      label='Rows'),
                        Item('skiprows',  label='Skip rows'),
                        Item('comments',  label='Comments'),
                        title = 'Text file options...',
                        buttons = [OKButton, CancelButton],
                        width = 0.2)

    array_view = View(Item('data', show_label = False,
                           editor = ArrayViewEditor(titles=[''],
                                                    format='%s',
                                                    font = 'Arial 10',
                                                    show_index = False)),
                      title = 'Array preview...',
                      width = 0.3,
                      height = 0.5,
                      buttons = [OKButton, CancelButton],
                      resizable = True)
    
    all_view = View(Item('filename', label="  File name", style='simple'),
                    UItem('show_options', label = 'Show/Hide options...'),
                    Item('skiprows',  label='Skip rows', visible_when='show_options_status'),
                    Item('columns',   label='Columns', visible_when='show_options_status'),
                    Item('rows',      label='Rows', visible_when='show_options_status'),
                    Item('delimiter', label='Delimiter', visible_when='show_options_status'),
                    Item('comments',  label='Comments', visible_when='show_options_status'),
                    Item('dtype',     label='Data type', visible_when='show_options_status'),
                    Item('decimal',   label='Decimal', visible_when='show_options_status and dtype=="float"'),
                    UItem('preview', label='Preview...'),
                    title = 'Load array...',
                    buttons = [OKButton, CancelButton],
                    handler = LoadTxtHandler(),
                    width = 0.25,
                    height = 0.3,
                    resizable=True,
                    scrollable=True)


# Do tests
if __name__ == "__main__":
    l = LoadTxt()
    l.data = np.array([[]])
    l.filename = 'black-scholes-input.dat'
    l.load()
    l.configure_traits(view = 'all_view')