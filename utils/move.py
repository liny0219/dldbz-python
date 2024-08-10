from utils.config_loader import config_loader
import utils.loger as loger

class MoveEngine:
    def __init__(self, controller):
        self.controller = controller
        self.interval= config_loader.get('move.interval')
        self.left    = config_loader.get('move.left')
        self.right   = config_loader.get('move.right')
        self.top     = config_loader.get('move.top')
        self.bottom  = config_loader.get('move.bottom')

    def run_to_left(self):
        loger.log_debug('正在执行向左跑')
        self.controller.swipe(*self.right, *self.left)
    
    def run_to_right(self):
        loger.log_debug('正在执行向右跑')
        self.controller.swipe(*self.left, *self.right)

    def run_to_top(self):
        loger.log_debug('正在执行向上跑')
        self.controller.swipe(*self.bottom, *self.top)

    def run_to_bottom(self):
        loger.log_debug('正在执行向下跑')
        self.controller.swipe(*self.top, *self.bottom)

    def move_x(self):
        loger.log_info('正在左右跑')
        self.run_to_left()
        self.controller.sleep_milliseconds(self.interval)
        self.run_to_right()
        self.controller.sleep_milliseconds(self.interval)

    def move_y(self):
        loger.log_info('正在上下跑')
        self.run_to_top()
        self.controller.sleep_milliseconds(self.interval)
        self.run_to_bottom()
        self.controller.sleep_milliseconds(self.interval)
