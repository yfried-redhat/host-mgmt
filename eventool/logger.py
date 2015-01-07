import logging

__author__ = 'yfried'

LOGGER_NAME = "event_tool.log"


# set up logging to file - see previous section for more details
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename=LOGGER_NAME,
    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# # tell the handler to use this format
# console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

getLogger = logging.getLogger

LOG = logging.getLogger(LOGGER_NAME)

logging.getLogger("paramiko").setLevel(logging.WARNING)