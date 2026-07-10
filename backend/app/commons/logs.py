import logging
import sys
import inspect

import pydantic_settings


class _Settings(pydantic_settings.BaseSettings):
    log_level: str = "INFO"


_SETTINGS = _Settings()

_LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[94m",    # Blue
        logging.INFO: "\033[92m",     # Green
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",    # Red
        logging.CRITICAL: "\033[95m", # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        log_fmt = (
            f"{color}%(asctime)s [%(levelname)s] "
            f"%(module)s.py:%(lineno)d - %(message)s{self.RESET}"
        )
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


_logger_instance: logging.Logger | None = None  # Singleton instance


def get_logger(level: int = _LOG_LEVEL_MAP.get(_SETTINGS.log_level, logging.INFO)) -> logging.Logger:
    global _logger_instance

    if _logger_instance is not None:
        return _logger_instance

    # Infer the caller's module name from the stack
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    module_name = module.__name__ if module else "default"

    logger = logging.getLogger(module_name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColorFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    _logger_instance = logger
    return logger
