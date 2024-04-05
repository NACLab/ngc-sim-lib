import logging
import sys
from ngcsimlib.configManager import GlobalConfig

def _concatArgs(*args, **kwargs):
    """Internal Decorator for concatenating arguments into a single string"""

    def inner(func):
        def wrapped(*wargs, sep=" ", end="", **kwargs):
            msg = sep.join(str(a) for a in wargs) + end
            return func(msg, **kwargs)

        return wrapped

    return inner


_ngclogger = logging.getLogger("ngclogger")


def init_logging():
    loggingConfig = GlobalConfig.get_config("logging")
    if loggingConfig is None:
        loggingConfig = {"logging_file": None,
                         "logging_level": logging.WARNING,
                         "hide_console": False}

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
        file_handler = logging.FileHandler(filename=loggingConfig.get("logging_file", None))
        file_handler.setFormatter(formatter)
        _ngclogger.addHandler(file_handler)


@_concatArgs()
def warn(msg):
    _ngclogger.warning(msg)


@_concatArgs()
def error(msg):
    _ngclogger.error(msg)
    raise RuntimeError(msg)


@_concatArgs()
def critical(msg):
    _ngclogger.critical(msg)
    raise RuntimeError(msg)


@_concatArgs()
def info(msg):
    _ngclogger.info(msg)
