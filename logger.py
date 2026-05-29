import os
import logging
from logging.handlers import RotatingFileHandler


# create a new logger with a specific handler if it does not exist
def get_logger(name):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    # Terminal handler — INFO and above only
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    # Ensure logs directory exists before writing to it
    os.makedirs("logs", exist_ok=True)

    # File handler — DEBUG and above (full detail)
    file_handler = RotatingFileHandler(
        f"logs/{name}.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger

# log a message to the specified logger with a given log level
def log(name, message, level=logging.INFO):
    logger = get_logger(name)
    logger.log(level, message)
