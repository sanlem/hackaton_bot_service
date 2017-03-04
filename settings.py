import logging
from tornado.options import define


define('port', default=8000)
define('host', default='0.0.0.0')
log_file = 'bot_service.log'
define('log_file', default=log_file)

logger = logging.getLogger('')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(log_file)
console_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# logger.removeHandler(logger.handlers[0])
logger.addHandler(file_handler)
logger.addHandler(console_handler)
