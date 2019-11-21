import errno
import logging
import os
import socket
import sys
from time import time as now


def wait_net_service(server, port, timeout=None):
    s = socket.socket()

    if timeout:
        end = now() + timeout

    while True:
        try:
            if timeout:
                next_timeout = end - now()  # time left until the `end`
                if next_timeout < 0:
                    # the `end` checkpoint already reached
                    return False
                else:
                    s.settimeout(next_timeout)

            s.connect((server, port))

        # TODO test on Windows, with different timeouts
        #      https://bugs.python.org/issue5293
        # except socket.timeout:
        #     return False

        except socket.error as err:
            # catch timeout exception from underlying network library
            # this one is different from socket.timeout
            if (type(err.args) != tuple or
                    (#err[0] != errno.ETIMEDOUT and
                     err[0] != errno.ECONNREFUSED)):
                raise
            # if err[0] == errno.ECONNREFUSED:
            #     s = socket.socket()
            s = socket.socket()
        else:
            s.close()
            return True


def wrap_subprocess(wrapped_function, verbose=True):
    def wrapper(*args, **kwargs):
        if not verbose:
            f = open(os.devnull, 'w')
            sys.stdout = f
            sys.stderr = f

            logging_config = {
                'handlers': {
                    'h': {
                        'class': 'logging.NullHandler',
                    },
                },
                'loggers': {
                    '': {
                        'handlers': ['h'],
                    },
                },
                'version': 1,
            }
            logging.config.dictConfig(logging_config)

        wrapped_function(*args, **kwargs)

    return wrapper


def parse_command_line_bool_arg(arg):
    upper_arg = str(arg).upper()
    if 'TRUE'.startswith(upper_arg):
        return True
    elif 'FALSE'.startswith(upper_arg):
        return False
    else:
        return bool(arg)
