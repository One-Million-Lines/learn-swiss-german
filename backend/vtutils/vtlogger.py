from sys import stdout, stderr
import logging
import json
import datetime
import traceback
from vtutils.misc import make_dict_json_serializable

LOGGER_NAME = "main"
FILTERS = []


class VTLogger(logging.Logger):

    def __init__(self, name):
        super(VTLogger, self).__init__(name)

    def remove_curly(self, msg):
        if msg and msg.startswith("{"):
            msg = msg[1:]
        if msg and msg.endswith("}"):
            msg = msg[:-1]
        return msg

    def format_msg(self, msg, *args, **kwargs):
        log_object = {}
        try:
            if msg and isinstance(msg, str):
                log_object["msg"] = msg
            passed_kwargs = {}
            if kwargs:
                for item in kwargs:
                    if item.endswith("_id") and isinstance(kwargs[item], str) and kwargs[item].isdigit():
                        kwargs[item] = int(kwargs[item])
                if "exc_info" in kwargs:
                    passed_kwargs = kwargs.pop("exc_info")
                if "extra" in kwargs:
                    passed_kwargs = kwargs.pop("extra")
                kwargs = make_dict_json_serializable(kwargs)
                log_object.update(kwargs)
            return log_object, passed_kwargs
        except Exception as e:
            self.error("Error formating log msg " + (msg if isinstance(msg, str) else '') + str(e))
            return {}, {}

    def debug(self, _msg, *args, **kwargs):
        log_object, passed_kwargs = self.format_msg(_msg, *args, **kwargs)
        super(VTLogger, self).debug(
            self.remove_curly(json.dumps(log_object)), *args, **passed_kwargs)

    def info(self, _msg, *args, **kwargs):
        log_object, passed_kwargs = self.format_msg(_msg, *args, **kwargs)
        super(VTLogger, self).info(
            self.remove_curly(json.dumps(log_object)), *args, **passed_kwargs)

    def error(self, _msg, *args, **kwargs):
        log_object, passed_kwargs = self.format_msg(_msg, *args, **kwargs)
        if "exc" not in log_object:
            log_object["err_type"] = "custom"
        else:
            log_object["err_type"] = type(log_object["exc"]).__name__
            log_object["err_details"] = repr(log_object["exc"])
            log_object["traceback"] = traceback.format_exc()
            del log_object["exc"]
        try:
            super(VTLogger, self).error(
                self.remove_curly(json.dumps(log_object)), *args, **passed_kwargs)
        except Exception as e:
            self.error("error_format_log", original_msg=repr(log_object), exc=e)


class AppFilter(logging.Filter):
    def __init__(self, hostname=None, proc_id=None):
        super(AppFilter, self).__init__()
        self._hostname = hostname
        self._proc_id = proc_id

    def filter(self, record):
        record.host = self._hostname
        record.proc_id = self._proc_id
        return True


class VT4Formatter(logging.Formatter):
    converter = datetime.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        t = ct.strftime("%Y-%m-%dT%H:%M:%S")
        s = "%s.%03d" % (t, record.msecs)
        return s


def initLog(logger_name, default_level="debug", host="localhost", proc_id=0):
    logging.setLoggerClass(VTLogger)
    debug_levels = {
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "error": logging.ERROR
    }
    logger = logging.getLogger(logger_name)
    logger.setLevel(debug_levels[default_level])

    debug_fh = logging.StreamHandler(stream=stdout)
    error_fh = logging.StreamHandler(stream=stderr)

    filter = AppFilter(hostname=host, proc_id=proc_id)
    logger.addFilter(filter)
    global FILTERS
    FILTERS = logger.filters
    debug_fh.setLevel(logging.DEBUG)
    error_fh.setLevel(logging.ERROR)
    std_formatter = VT4Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s",'
        ' "name": "%(name)s-%(proc_id)s", %(message)s}')

    debug_fh.setFormatter(std_formatter)
    error_fh.setFormatter(std_formatter)

    logger.addHandler(debug_fh)
    logger.propagate = False

    logger.info("Logging initialized")
    global LOGGER_NAME
    LOGGER_NAME = logger_name
    return logger


def getLog(existing_log_name=""):
    logger = None
    if LOGGER_NAME != "" and existing_log_name:
        logger = logging.getLogger("{0}.{1}".format(LOGGER_NAME, existing_log_name))
        for filter in FILTERS:
            if filter not in logger.filters:
                logger.addFilter(filter)
    elif LOGGER_NAME and not existing_log_name:
        logger = logging.getLogger(LOGGER_NAME)
    else:
        logger = logging.getLogger(existing_log_name)
    return logger
