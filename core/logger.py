import logging
import sys


# logging.basicConfig(
#     level=logging.DEBUG,
#     format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
#            '%(lineno)d - %(name)s - %(message)s'
# )
# logger = logging.getLogger(__name__)
# stdout_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(stdout_handler)

logger = logging.getLogger('proj')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)