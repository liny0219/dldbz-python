from enum import Enum
from functools import partial
from utils.status import BUTTON_STATUS
from utils.config_loader import config_loader
from utils.wait import wait_until, wait_until_not
import utils.loger as loger

class Move_Direct(Enum):
        TO_RIGHT   = 0
        TO_LEFT    = 1
        TO_TOP     = 2
        TO_BOTTOM  = 3
        LEFT_RIGHT = 4
        TOP_BOTTOM = 5
        

class World:
    def __init__(self, controller, comparator):
        self.controller = controller
        self.comparator = comparator
        self.confirm_coord = \
            config_loader.get("general.confirm_coord")
        
        self.check_world_ui_refs  = \
            config_loader.get("world.check_world_ui_refs")
        self.check_menu1_ui_refs  = \
            config_loader.get("world.check_menu1_ui_refs")   # 检测世界图片1
        self.check_menu2_ui_refs  = \
            config_loader.get("world.check_menu2_ui_refs")   # 检测世界图片2
            
        self.rest_active_refs  = \
            config_loader.get("world.rest_active_refs")    # 检测休息按钮（可用）图片
        self.rest_disable_refs  = \
            config_loader.get("world.rest_disable_refs")   # 检测休息按钮（不可用）图片
        
        
        self.move_param = {"interval": config_loader.get('move.interval'),
                           "left"    : config_loader.get('move.left'),
                           "right"   : config_loader.get('move.right'),
                           "bottom"  : config_loader.get('move.bottom')}
    
    def _check_have_menu1(self):
        return self.comparator.template_in_picture(self.check_menu1_ui_refs) is not None
    
    def _check_have_menu2(self):
        return self.comparator.template_in_picture(self.check_menu2_ui_refs) is not None
    
    def _check_have_menu(self):
        have_menu1 = self._check_have_menu1()
        have_menu2 = self._check_have_menu2()
        return have_menu1 or have_menu2
    
    def _check_in_world(self):
        return self.comparator.rotates_template_in_picture(self.check_world_ui_refs) is not None
    
    def rest_status(self) -> BUTTON_STATUS:
        self.controller.press(self.confirm_coord) # 尝试停止移动
        if not self._check_have_menu():  # 没有菜单
            return BUTTON_STATUS.UNKNOWN
        wait_until(self._check_have_menu1, [partial(self.controller.press, self.confirm_coord)]) # 等待菜单1加载
        
        # 因为休息不可用状态判断更为严格，所以先判断是否为disable
        if self.comparator.template_in_picture(self.rest_disable_refs): # 休息不可用状态
            return BUTTON_STATUS.DISABLE
        if self.comparator.template_in_picture(self.rest_active_refs): # 休息可用状态
            return BUTTON_STATUS.ACTIVE
        return BUTTON_STATUS.NOT_EXIST  # 不存在
        
        
    def _move(self, direct: Move_Direct) -> None:
        if direct == Move_Direct.TO_RIGHT:
            self._swipe(self.left, self.right, "正在从左往右移动")
        elif direct == Move_Direct.TO_LEFT:
            self._swipe(self.right, self.left, "正在从右往左移动")
        elif direct == Move_Direct.TO_TOP:
            self._swipe(self.bottom, self.top, "正在从下往上移动")
        elif direct == Move_Direct.TO_BOTTOM:
            self._swipe(self.top, self.bottom, "正在从上往下移动")
        elif direct == Move_Direct.LEFT_RIGHT:
            self._move_x("正在左右来回跑")
        elif direct == Move_Direct.TOP_BOTTOM:
            self._move_y("正在上下来回跑")
            
    def move_once(self, direct: Move_Direct) -> None:
        wait_until(self._check_have_menu1, [partial(self.controller.press, self.confirm_coord)]) # 等待菜单1加载
        self._move(direct)
            
    def move_until_not_in_world(self, direct: Move_Direct) -> None:
        wait_until(self._check_in_world1, [partial(self.controller.press, self.confirm_coord)]) # 等待菜单1加载
        wait_until_not(self._check_in_world, [partial(self._move, direct)])

    def _swipe(self, start, end, log_message=''):
        if(log_message):
            loger.log_info(log_message)
        self.controller.swipe(start, end)
        self.controller.sleep_ms(self.interval)

    def _move_x(self, log_message=''):
        self._swipe(self.right, self.left, log_message)
        self._swipe(self.left, self.right)

    def _move_y(self, log_message=''):
        self._swipe(self.bottom, self.top, log_message)
        self._swipe(self.top, self.bottom)