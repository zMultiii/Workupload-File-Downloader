import logging
from datetime import datetime
import os


workdir = "./logs"
if not os.path.exists(workdir):
    os.makedirs(workdir)

today = datetime.now()
fileName = f'{workdir}/{today.date()}.log'

# Handler for file logging
# File's name follow 'YYYY-MM-DD.log'
fileHandler = logging.FileHandler(fileName)
fileHandler.setLevel(logging.DEBUG)

# Handler for console logging
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)


# Apply config
logging.basicConfig(
    format='%(asctime)s [%(threadName)-12.12s / %(levelname)-8.8s] -> %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG,
    handlers=[fileHandler, consoleHandler]
)
logger = logging.getLogger()
logger.addHandler(fileHandler)
logger.addHandler(consoleHandler)


def deb(s: str):
    logger.debug(s)


def info(s: str):
    logger.info(s)


def warn(s: str):
    logger.warning(s)


def err(s: str):
    logger.error(s)


def crit(s: str):
    logger.critical(s)


def ex(e: Exception):
    logger.exception(msg=e)


def end_of_line():
    with open(fileName, 'a') as log:
        log.write('/-----------------------/\n')
