import logging
import traceback
from utils.config_loader import config_loader

# 根据环境变量判断模式
DEBUG_MODE = config_loader.get('debug')
print(DEBUG_MODE)

# 设置日志配置
if DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
else:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

# 定义一个统一的日志记录器
logger = logging.getLogger(__name__)

def log_exception(e : Exception):
    logger.error(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
    

def log_debug(message):
    if DEBUG_MODE:
        logger.debug(message)

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)