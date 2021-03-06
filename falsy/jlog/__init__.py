import logging.config
import logging

import datetime

import collections

from falsy.termcc.termcc import red


class ColoredRecord(object):
    class __dict(collections.defaultdict):
        def __missing__(self, name):
            try:
                return parse_colors(name)
            except Exception:
                raise KeyError("{} is not a valid record attribute "
                               "or color sequence".format(name))

    def __init__(self, record):
        # Replace the internal dict with one that can handle missing keys
        self.__dict__ = self.__dict()
        self.__dict__.update(record.__dict__)

        self.__record = record

    def __getattr__(self, name):
        return getattr(self.__record, name)


class MyFormatter(logging.Formatter):
    converter = datetime.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


# from colorlog import ColoredFormatter

default_formats = {
    '%': '%(log_color)s%(levelname)s:%(name)s:%(message)s',
    '{': '{log_color}{levelname}:{name}:{message}',
    '$': '${log_color}${levelname}:${name}:${message}'
}
import sys

default_log_colors = {
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


# Returns escape codes from format codes
def esc(*x):
    return '\033[' + ';'.join(x) + 'm'


# The initial list of escape codes
escape_codes = {
    'reset': esc('0'),
    'bold': esc('01'),
}

# The color names
COLORS = [
    'black',
    'red',
    'green',
    'yellow',
    'blue',
    'purple',
    'cyan',
    'white'
]

PREFIXES = [
    # Foreground without prefix
    ('3', ''), ('01;3', 'bold_'),

    # Foreground with fg_ prefix
    ('3', 'fg_'), ('01;3', 'fg_bold_'),

    # Background with bg_ prefix - bold/light works differently
    ('4', 'bg_'), ('10', 'bg_bold_'),
]

for prefix, prefix_name in PREFIXES:
    for code, name in enumerate(COLORS):
        escape_codes[prefix_name + name] = esc(prefix + str(code))


def parse_colors(sequence):
    """Return escape codes from a color sequence."""
    return ''.join(escape_codes[n] for n in sequence.split(',') if n)


def parse_colors(sequence):
    print('>>>>>>>>1',sequence)
    a=''.join(escape_codes[n] for n in sequence.split(',') if n)
    print('>>>>>>>>2')
    return a


class ColoredFormatter1(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%',
                 log_colors=None, reset=True,
                 secondary_log_colors=None):
        if fmt is None:
            if datetime.sys.version_info > (3, 2):
                fmt = default_formats[style]
            else:
                fmt = default_formats['%']

        if sys.version_info > (3, 2):
            super(ColoredFormatter1, self).__init__(fmt, datefmt, style)
        elif sys.version_info > (2, 7):
            super(ColoredFormatter1, self).__init__(fmt, datefmt)
        else:
            logging.Formatter.__init__(self, fmt, datefmt)

        self.log_colors = (
            log_colors if log_colors is not None else default_log_colors)
        print(self.log_colors)
        self.secondary_log_colors = secondary_log_colors
        self.reset = reset

    def color(self, log_colors, level_name):
        """Return escape codes from a ``log_colors`` dict."""
        return parse_colors(log_colors.get(level_name, ""))

    def format(self, record):
        """Format a message from a record object."""
        record = ColoredRecord(record)
        record.log_color = self.color(self.log_colors, record.levelname)

        # # Set secondary log colors
        # if self.secondary_log_colors:
        #     for name, log_colors in self.secondary_log_colors.items():
        #         color = self.color(log_colors, record.levelname)
        #         setattr(record, name + '_log_color', color)

        message = super(ColoredFormatter1, self).format(record)

        if self.reset and not message.endswith(escape_codes['reset']):
            message += escape_codes['reset']

        return message


LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s.%(msecs)03d] - [%(levelname)-8s] - [%(name)-16s] - [%(message)s]',
            'datefmt': '%Y-%m-%d %H:%M:%S %Z%z'
        },
        'colored': {
            '()': 'falsy.jlog.ColoredFormatter1',
            'format': '[%(asctime)s.%(msecs)03d] - [%(levelname)-8s] - [%(name)-16s] - [%(message)s]',
            # 'format': '[%(blue)s%(asctime)s.%(msecs)03d%(reset)s] - [%(log_color)s%(levelname)-8s%(reset)s] - [%(purple)s%(name)-16s%(reset)s] - [%(cyan)s%(message)s%(reset)s]',
            'datefmt': '%Y-%m-%d %H:%M:%S %Z%z',
        },

        'log_colors': {
            'DEBUG': 'white',
            'INFO': 'bold_green',
            'WARNING': 'bold_yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'red,bg_white'
        }
    },
    'handlers': {
        'rotate_file': {
            'level': 'INFO',
            'filters': None,
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'falsy.log',
            'formatter': 'standard'
        },
        'console': {
            'level': 'DEBUG',
            'filters': None,
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'colored'
        },
    },
    'loggers': {
        'falsy': {
            'handlers': ['rotate_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# class JLog:
#     def __init__(self, config=LOG_CONFIG):

# if __name__ == '__main__':
