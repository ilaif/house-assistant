import logging
import os


def get_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)

    file_handler = logging.FileHandler('/var/log/house-assistant.log')
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger


def is_rpi():
    return os.uname()[4].startswith("arm")
