########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

import os
import sys
import tempfile

STDOUT = 1
STDERR = 2

class Redirector(object):
    def __init__(self, fd=STDOUT):
        self.fd = fd
        self.started = False

    def start(self):
        if not self.started:
            self.tmpfd, self.tmpfn = tempfile.mkstemp()

            self.oldhandle = os.dup(self.fd)
            os.dup2(self.tmpfd, self.fd)
            os.close(self.tmpfd)

            self.started = True

    def flush(self):
        if self.fd == STDOUT:
            sys.stdout.flush()
        elif self.fd == STDERR:
            sys.stderr.flush()

    def stop(self):
        if self.started:
            self.flush()
            os.dup2(self.oldhandle, self.fd)
            os.close(self.oldhandle)
            tmpr = open(self.tmpfn, 'rb')
            output = tmpr.read()
            tmpr.close()  # this also closes self.tmpfd
            os.unlink(self.tmpfn)

            self.started = False
            return output
        else:
            return None

class RedirectorOneFile(object):
    def __init__(self, fd=STDOUT):
        self.fd = fd
        self.started = False
        self.inited = False

        self.initialize()

    def initialize(self):
        if not self.inited:
            self.tmpfd, self.tmpfn = tempfile.mkstemp()
            self.pos = 0
            self.tmpr = open(self.tmpfn, 'rb')
            self.inited = True

    def start(self):
        if not self.started:
            self.oldhandle = os.dup(self.fd)
            os.dup2(self.tmpfd, self.fd)
            self.started = True

    def flush(self):
        if self.fd == STDOUT:
            sys.stdout.flush()
        elif self.fd == STDERR:
            sys.stderr.flush()

    def stop(self):
        if self.started:
            self.flush()
            os.dup2(self.oldhandle, self.fd)
            os.close(self.oldhandle)
            output = self.tmpr.read()
            self.pos = self.tmpr.tell()
            self.started = False
            return output
        else:
            return None

    def close(self):
        if self.inited:
            self.flush()
            self.tmpr.close()  # this also closes self.tmpfd
            os.unlink(self.tmpfn)
            self.inited = False
            return output
        else:
            return None


import os
import sys
from contextlib import contextmanager


@contextmanager
def redirect_stdout(new_target):
    old_target, sys.stderr = sys.stdout, new_target  # replace sys.stdout
    try:
        yield new_target # run some code with the replaced stdout
    finally:
        sys.stdout = old_target # restore to the previous value


def fileno(file_or_fd):
    fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
    if not isinstance(fd, int):
        raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
    return fd


@contextmanager
def stdout_redirected(to=os.devnull, stdout=None):
    if stdout is None:
       stdout = sys.stdout

    stdout_fd = fileno(stdout)
    # copy stdout_fd before it is overwritten
    #NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied: 
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stdout_fd)  # $ exec >&to
        except ValueError:  # filename
            with open(to, 'wb') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
        try:
            yield stdout # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            #NOTE: dup2 makes stdout_fd inheritable unconditionally
            stdout.flush()
            os.dup2(copied.fileno(), stdout_fd)  # $ exec >&copied


@contextmanager
def stderr_redirected(to=os.devnull, stdout=None):
    if stdout is None:
       stdout = sys.stderr

    stdout_fd = fileno(stdout)
    # copy stdout_fd before it is overwritten
    #NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied: 
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stdout_fd)  # $ exec >&to
        except ValueError:  # filename
            with open(to, 'wb') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
        try:
            yield stdout # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            #NOTE: dup2 makes stdout_fd inheritable unconditionally
            stdout.flush()
            os.dup2(copied.fileno(), stdout_fd)  # $ exec >&copied
