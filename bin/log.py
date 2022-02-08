# log.py

import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
)

# get the path to the root of the project
Root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(Root, "Logs"), exist_ok=True)
LOG_FILE = os.path.join(Root, "Logs", "ReSubBot.log")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    console_handler.setLevel(logging.DEBUG)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when="H", interval=8, encoding="UTF-8"
    )
    file_handler.setFormatter(FORMATTER)
    file_handler.setLevel(logging.DEBUG)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(
        logging.DEBUG
    )  # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary
    # to propagate the error up to parent
    logger.propagate = False
    return logger
