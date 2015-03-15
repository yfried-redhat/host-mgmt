import logging
import sys
import traceback

__author__ = 'yfried'

LOGGER_NAME = "event_tool.log"


# set up logging to file - see previous section for more details
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename=LOGGER_NAME,
    filemode='w')
# define a Handler which writes WARN messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.CRITICAL)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# # tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

logging.getLogger("paramiko").setLevel(logging.WARNING)

getLogger = logging.getLogger

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.WARN)

# LOG = getLogger(__name__)


def hideTrace(log):
    """Creates excepthook that sends traceback to log.debug and Exception to
     stderr.

    :param log: logger to log trace
    """
    def my_excepthook(exc_type, exc_value, exc_traceback):
        # sends full exception with trace to log
        # TODO(yfried): get rid of "None" being printed to log
        formated_exception = traceback.format_exception(exc_type, exc_value,
                                                        exc_traceback)
        ex_str = "".join(formated_exception)
        log.exception(ex_str)

        # # sends exception type and message (without trace) to CRITICAL log
        # ex_msg = "".join(traceback.format_exception(exc_type, exc_value, None))
        # log.critical(ex_msg)

        # sends exception (without trace) to std.err
        traceback.print_exception(exc_type, exc_value, None)

    sys.excepthook = my_excepthook
