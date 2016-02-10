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
from pyface.api import GUI
import logging
import sys, uuid


class LogsLoggerHandler(logging.Handler):
    def __init__(self, logs_cls, level=logging.DEBUG):
        logging.Handler.__init__(self, level=level)
        self.logs_cls = logs_cls

    def emit(self, record):
        msg = self.format(record)
        self.logs_cls._append_log(msg)


class Logger(HasTraits):
    _logs = Code
    _clear = Button
    logger = Instance(logging.Logger, transient=True)
    handler = Instance(logging.Handler, transient=True)

    def __init__(self, level=logging.DEBUG, **traits):
        HasTraits.__init__(self, **traits)
        name = uuid.uuid4().hex  # name in __init__ args?
        logger = logging.getLogger(name)
        handler = LogsLoggerHandler(self, level)
        logger.addHandler(handler)
        logger.setLevel(level)
        self.handler = handler
        self.logger = logger
        self._lines = 1000000000000  # for auto_scroll
        self._progress_started = False
        self._progress_logs = ''

    @property
    def logs(self):
        return self._logs

    def _append_log(self, msg, endline = '\n'):
        def toappend():
            if self._progress_started:
                self._progress_logs += msg + endline
            else:
                self._logs += msg + endline
        GUI.invoke_later(toappend)  # to be thread safe when logs are displayed in gui


    def _set_log(self, msg, endline = '\n'):
        def toset():
            self._logs = msg + endline
        GUI.invoke_later(toset)  # to be thread safe when logs are displayed in gui

    def clear(self):
        self._set_log('', '')
        self._progress_logs = ''

    def progress_start(self, msg):
        import thread, time
        if self._progress_started:
            raise ValueError("Cannot start progress twice!")  # At the moment
        def toprogress():
            messages = [msg + ': ' + s for s in "/-\|/-\|"]
            self._progress_logs = self.logs
            self._progress_started = True
            while self._progress_started:
                for m in messages:
                    if self._progress_started:
                        self._set_log(self._progress_logs + m)
                        time.sleep(0.05)
                    else:
                        break
        thread.start_new_thread(toprogress, ())
        #GUI.invoke_later(thread.start_new_thread, toprogress, ())

    def progress_stop(self):
        if not self._progress_started:
            raise ValueError("Progress is not started!")
        self._set_log(self._progress_logs.strip())
        self._progress_logs = ''   # this should be safe because progress_logs are nor displayed
        self._progress_started = False

    def __clear_fired(self):
        self.clear()

    traits_view = View(UItem('_logs',
                             style  = 'readonly',
                             editor = CodeEditor(show_line_numbers = False,
                                                 selected_color    = 0xFFFFFF,
                                                 selected_line = '_lines',
                                                 auto_scroll = True,
                                                 lexer = 'none'
                                                 ),
                             resizable = True,
                             ),
                       #  UItem('_clear', label="Clear"),
                       )


if __name__ == '__main__':
    class TestClass(HasTraits):
        logger = Instance(Logger, ())
        add_text = Button
        i = Int(0)

        def _add_text_fired(self):
            self.logger.logger.info("Some text is added %i" %self.i)
            self.i += 1

        traits_view = View(UItem('logger', style='custom'), 
                           UItem('add_text'),
                           buttons = ['OK', 'Cancel'],
                           resizable = True,
                           width = 0.4,
                           height = 0.3,
                           )
    t = TestClass()
    t.configure_traits()

