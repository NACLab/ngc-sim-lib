from ngcsimlib.configManager import get_config
import logging
import sys
from datetime import datetime


def _concatArgs(func):
    """Internal Decorator for concatenating arguments into a single string"""
    def wrapped(*wargs, sep=" ", end="", **kwargs):
        msg = sep.join(str(a) for a in wargs) + end
        return func(msg, **kwargs)

    return wrapped


_ngclogger = logging.getLogger("ngclogger")

_mapped_calls = {}

def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    Credit: https://stackoverflow.com/a/35804945

    Args:
        levelName: The custom level name

        levelNum: The custom level number

        methodName: The name of the method
    """


    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

    _mapped_calls[levelNum] = getattr(_ngclogger, methodName)
    _mapped_calls[levelName] = getattr(_ngclogger, methodName)

def init_logging():
    loggingConfig = get_config("logging")
    if loggingConfig is None:
        loggingConfig = {"logging_file": None,
                         "logging_level": logging.WARNING,
                         "hide_console": False,
                         "custom_levels": {"ANALYSIS": 25}}

    if loggingConfig.get("custom_levels", None) is not None:
        for level_name, level_num in loggingConfig.get("custom_levels", {}).items():
            addLoggingLevel(level_name.upper(), level_num)


    if isinstance(loggingConfig.get("logging_level", None), str):
        loggingConfig["logging_level"] = \
            logging.getLevelName(loggingConfig.get("logging_level", "").upper())

    logging_level = loggingConfig.get("logging_level", logging.WARNING)
    _ngclogger.setLevel(logging_level)
    formatter = logging.Formatter("%(levelname)s - %(message)s")

    if not loggingConfig.get("hide_console", False):
        err_stream_handler = logging.StreamHandler(sys.stderr)
        err_stream_handler.setFormatter(formatter)
        _ngclogger.addHandler(err_stream_handler)

    if loggingConfig.get("logging_file", None) is not None:
        with open(loggingConfig.get("logging_file", None), "a+") as fp:
            fp.write(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
                     f"New Log {f'{datetime.utcnow():%m/%d/%Y %H:%M:%S}'}"
                     f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        file_handler = logging.FileHandler(filename=loggingConfig.get("logging_file", None))
        file_handler.setFormatter(formatter)
        _ngclogger.addHandler(file_handler)


@_concatArgs
def warn(msg):
    """
    Logs a warning message
    This is decorated to have the same functionality of python's print argument concatenation

    Args:
        msg: message to log
    """
    _ngclogger.warning(msg)


@_concatArgs
def error(msg):
    """
    Logs an error message
    This is decorated to have the same functionality of python's print argument concatenation

    Args:
        msg: message to log
    """
    _ngclogger.error(msg)
    raise RuntimeError(msg)


@_concatArgs
def critical(msg):
    """
    Logs a critical message
    This is decorated to have the same functionality of python's print argument concatenation

    Args:
        msg: message to log
    """
    _ngclogger.critical(msg)
    raise RuntimeError(msg)


@_concatArgs
def info(msg):
    """
    Logs an info message
    This is decorated to have the same functionality of python's print argument concatenation

    Args:
        msg: message to log
    """
    _ngclogger.info(msg)


@_concatArgs
def debug(msg):
    """
    Logs a debug message
    This is decorated to have the same functionality of python's print argument concatenation

    Args:
        msg: message to log
    """
    _ngclogger.debug(msg)


@_concatArgs
def custom_log(msg, logging_level=None):
    """
    Logs to a user defined logging level. This will only work for user defined
    levels if a builtin logging level is desired please use on of the builtin
    logging methods found in this file. To defined logging levels add them to the
    configuration file of your project. To add levels here add the map of
    `logging_levels` to the top level logging object and have the key be the new
    logging level name, and the value be the numerical logging value. To see all
    build in logging levels look at the builtin python logger package.


    This is decorated to have the same functionality of python's print argument concatenation

    Args:
        msg: The message to log

        logging_level: The user defined logging level.
    """
    if isinstance(logging_level, str):
        logging_level = logging_level.upper()

    if logging_level is None:
        warn("No logging level passed into message")
    elif logging_level not in _mapped_calls.keys():
        warn("Attempted to log to undefined level", logging_level)
    else:
        _mapped_calls[logging_level](msg)

