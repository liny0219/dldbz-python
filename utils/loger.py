import logging
import traceback

# 根据环境变量判断模式
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# 定义一个统一的日志记录器
loger = logging.getLogger(__name__)

def log_exception(e : Exception):
    loger.error(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
    
def log_debug(message):
    print(message)

def log_info(message):
    print(message)

def log_error(message):
    print(message)
# def log_debug(message):
#     loger.debug(message)

# def log_info(message):
#     loger.info(message)

# def log_error(message):
#     loger.error(message)