import logging
import subprocess
import sys
#from pyface.api import GUI

class ClassWithLogsHandler(logging.Handler):
    def __init__(self, class_with_logs, level=logging.DEBUG):
        logging.Handler.__init__(self)
        self.class_with_logs = class_with_logs
    
    def emit(self, record):
        msg = self.format(record)
        self.class_with_logs.logs_selected_line += msg.count('\n') + 2
        self.class_with_logs.logs += msg + '\n'
        #import time
        #time.sleep(0.1)


def create_logger(name, class_with_logs, level=logging.DEBUG):
    h = ClassWithLogsHandler(class_with_logs)
    logger = logging.getLogger(name)
    logger.addHandler(h)
    # the default formatter just returns the message
    logger.setLevel(level)
    return logger

if __name__ == '__main__':
    class TestClass(object):
        logs = ''
    t = TestClass()
    logger = create_logger('test', t)
    logger.info('Hello')
    logger.debug('Goodbye')
    print t.logs

