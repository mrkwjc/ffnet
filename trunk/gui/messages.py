########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

import pyface.api as pyface
import traceback as tb
import sys

def display_error(message='Error occured!', title='Error', traceback = False):
    msg = message
    # Check if we have an error
    etype, value, tbstr = sys.exc_info()
    emsg = ''
    if etype is not None:
        if not traceback:
            emsg = tb.format_exception_only(etype, value)
        else:
            emsg = tb.format_exception(etype, value, tbstr)
        emsg = ''.join(emsg)
        msg = msg + '\n\n' + emsg
    # display error
    pyface.error(None, msg, title=title)


def display_confirm(message, title=None, cancel=False):
    answer = pyface.confirm(None, message, title=title, cancel=cancel)
    if answer == pyface.YES:
        return True
    if answer == pyface.NO:
        return False
    if answer == pyface.CANCEL:
        return None