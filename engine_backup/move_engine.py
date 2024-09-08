from utils.config_loader import cfg_world
import utils.loger as loger

class MoveEngine:
    def __init__(self, controller):
        self.controller = controller
        self.interval= cfg_world.get('move.interval')
        self.left    = cfg_world.get('move.left')
        self.right   = cfg_world.get('move.right')
        self.top     = cfg_world.get('move.top')
        self.bottom  = cfg_world.get('move.bottom')

    def run_to_left(self):
        loger.log_debug('正在执行向左跑')
        self.controller.swipe(self.right, self.left)
    
    def run_to_right(self):
        loger.log_debug('正在执行向右跑')
        self.controller.swipe(self.left, self.right)

    def run_to_top(self):
        loger.log_debug('正在执行向上跑')
        self.controller.swipe(self.bottom, self.top)

    def run_to_bottom(self):
        loger.log_debug('正在执行向下跑')
        self.controller.swipe(self.top, self.bottom)

    def move_x(self):
        loger.log_info('正在左右跑')
        self.run_to_left()
        self.controller.sleep_ms(self.interval)
        self.run_to_right()
        self.controller.sleep_ms(self.interval)

    def move_y(self):
        loger.log_info('正在上下跑')
        self.run_to_top()
        self.controller.sleep_ms(self.interval)
        self.run_to_bottom()
        self.controller.sleep_ms(self.interval)
