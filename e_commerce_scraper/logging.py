import logging


class Logger:
    def __init__(self, config, fslogger, flogger):
        self.config = config
        self.fslogger = fslogger
        self.flogger = flogger

    def _get_loggers(self):
        loggers = []
        if self.config("verbose"):
            loggers.append(self.fslogger)
        else:
            loggers.append(self.flogger)
        return loggers

    def info(self, message):
        list(map(lambda x: x.info(message), self._get_loggers()))

    def error(self, message):
        list(map(lambda x: x.error(message), self._get_loggers()))

    def debug(self, message):
        list(map(lambda x: x.debug(message), self._get_loggers()))

    def warning(self, message):
        list(map(lambda x: x.warning(message), self._get_loggers()))

    def exception(self, message):
        list(map(lambda x: x.exception(message), self._get_loggers()))


class LoggerFactory:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.fslogger = self._get_file_stream_logger(self.config)
        self.flogger = self._get_file_logger(self.config)

    def get_logger(self):
        return Logger(self.config, self.fslogger, self.flogger)

    def _get_file_stream_logger(self, config):

        logger = logging.getLogger(name=f"{self.name}_fslogger")
        if not logger.hasHandlers():
            # add file handler
            formatter = logging.Formatter(config("logging_format"))
            fh = logging.FileHandler(config("logging_folder"))
            fh.setFormatter(formatter)
            logger.addHandler(fh)

            # add stream handler
            formatter = logging.Formatter(config("logging_format"))
            sh = logging.StreamHandler()
            # sh.setLevel(config('logging_level'))
            sh.setFormatter(formatter)
            logger.addHandler(sh)
            logger.setLevel(config("logging_level"))
        return logger

    def _get_file_logger(self, config):

        logger = logging.getLogger(name=f"{self.name}_flogger")
        if not logger.hasHandlers():
            formatter = logging.Formatter(config("logging_format"))
            fh = logging.FileHandler(config("logging_folder"))
            fh.setLevel(config("logging_level"))
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            logger.setLevel(config("logging_level"))
        return logger
