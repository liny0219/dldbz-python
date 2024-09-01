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
    def __init__(self, player):
        self.player = player
        self.controller = player.controller
        self.comparator = player.comparator
        self.moving     = False
        
        self.confirm_coord = \
            config_loader.get("general.confirm_coord")
        
        self.check_world_ui_refs  = \
            config_loader.get("world.check.check_world_ui_refs")
        self.check_menu1_ui_refs  = \
            config_loader.get("world.check.check_menu1_ui_refs")   # 检测世界图片1
        self.check_menu2_ui_refs  = \
            config_loader.get("world.check.check_menu2_ui_refs")   # 检测世界图片2
        self.check_in_battle_refs = \
            config_loader.get("battle.check.check_battle_ui_refs") # 检测在战斗中
            
        self.rest_active_refs  = \
            config_loader.get("world.button.rest_active_refs")    # 休息按钮（可用）图片
        self.rest_disable_refs  = \
            config_loader.get("world.button.rest_disable_refs")   # 休息按钮（不可用）图片
            
        
        
        self.move_param = {"interval": config_loader.get('world.move.interval'),
                           "left"    : config_loader.get('world.move.left'),
                           "right"   : config_loader.get('world.move.right'),
                           "top"     : config_loader.get('world.move.top'),
                           "bottom"  : config_loader.get('world.move.bottom')}
        
        self.check_starting_screen = config_loader.get('world.check.check_in_starting_screen')
        self.check_cross1 = config_loader.get('world.check.check_cross1')
        self.check_cross2 = config_loader.get('world.check.check_cross2')
        self.check_monopoly_option = config_loader.get('monopoly.check.check_monopoly_option')
        self.check_monopoly_end = config_loader.get('monopoly.check.check_monopoly_end')
        self.check_monopoly_end_confirm = config_loader.get('monopoly.check.check_monopoly_end_confirm')

    
    def _check_have_menu1(self):
        return self.comparator.template_in_screen(self.check_menu1_ui_refs)
    
    def _check_have_menu2(self):
        return self.comparator.template_in_screen(self.check_menu2_ui_refs)
    
    def _check_have_menu(self):
        have_menu1 = self._check_have_menu1()
        have_menu2 = self._check_have_menu2()
        return have_menu1 or have_menu2
    
    def _check_move_to_battle(self):
        return self.moving and self.comparator.template_in_screen(self.check_in_battle_refs)

    
    def rest_status(self) -> BUTTON_STATUS:
        self.controller.press(self.confirm_coord) # 尝试停止移动
        if not self._check_have_menu():  # 没有菜单
            return BUTTON_STATUS.UNKNOWN
        wait_until(self._check_have_menu1, [partial(self.controller.press, self.confirm_coord)]) # 等待菜单1加载
        
        # 因为休息不可用状态判断更为严格，所以先判断是否为disable
        if self.comparator.template_in_screen(self.rest_disable_refs): # 休息不可用状态
            return BUTTON_STATUS.DISABLE
        if self.comparator.template_in_screen(self.rest_active_refs): # 休息可用状态
            return BUTTON_STATUS.ACTIVE
        return BUTTON_STATUS.NOT_EXIST  # 不存在
    
    def _stop_move(self) -> None:
        wait_until(self._check_have_menu1, [partial(self.controller.press, self.confirm_coord)]) # 等待菜单1加载
        self.moving = False
    
    def _move(self, direct: Move_Direct) -> None:
        self.moving = True
        if direct == Move_Direct.TO_RIGHT:
            self._swipe(self.move_param["left"], self.move_param["right"], "正在从左往右移动")
        elif direct == Move_Direct.TO_LEFT:
            self._swipe(self.move_param["right"], self.move_param["left"], "正在从右往左移动")
        elif direct == Move_Direct.TO_TOP:
            self._swipe(self.move_param["bottom"], self.move_param["top"], "正在从下往上移动")
        elif direct == Move_Direct.TO_BOTTOM:
            self._swipe(self.move_param["top"], self.move_param["bottom"], "正在从上往下移动")
        elif direct == Move_Direct.LEFT_RIGHT:
            self._move_x("正在左右来回跑")
        elif direct == Move_Direct.TOP_BOTTOM:
            self._move_y("正在上下来回跑")
            
    def move_once(self, direct: Move_Direct) -> None:
        wait_until(self._check_have_menu1, [partial(self.controller.press, self.confirm_coord)]) # 等待菜单1加载
        self._move(direct)
            
    def move_until_not_in_world(self, direct: Move_Direct) -> None:
        wait_until(self._check_have_menu1, [partial(self.controller.press, self.confirm_coord)]) # 等待菜单1加载
        wait_until(self._check_move_to_battle, [partial(self._move, direct)])
        

    def _swipe(self, start, end, log_message=''):
        if(log_message):
            loger.log_info(log_message)
        self.controller.swipe(start, end)
        self.controller.sleep_ms(self.move_param["interval"])

    def _move_x(self, log_message=''):
        print(self.move_param["right"], self.move_param["left"])
        
        self._swipe(self.move_param["right"], self.move_param["left"], log_message)
        self._swipe(self.move_param["left"], self.move_param["right"])

    def _move_y(self, log_message=''):
        self._swipe(self.move_param["bottom"], self.move_param["top"], log_message)
        self._swipe(self.move_param["top"], self.move_param["bottom"])

    def check_in_starting_screen_and_start(self):
        in_starting = self.comparator.template_in_screen(self.check_starting_screen, return_center_coord=True)
        if in_starting:
            self.controller.press(in_starting)

    def check_and_cancel1(self):
        in_cross1 = self.comparator.template_in_screen(self.check_cross1, return_center_coord=True)
        if in_cross1:
            self.controller.press(in_cross1)

    def check_and_cancel2(self):
        in_cross2 = self.comparator.template_in_screen(self.check_cross2, return_center_coord=True)
        if in_cross2:
            self.controller.press(in_cross2)

    def check_and_cancel(self):
        self.check_and_cancel1()
        self.check_and_cancel2()

    def check_menu2_and_back_menu1(self):
        in_menu2 = self.comparator.template_in_screen(self.check_menu2_ui_refs)
        if in_menu2:
            self.controller.press(self.confirm_coord)

    def check_monopoly_and_leave(self):
        event = self.comparator.template_in_screen(self.check_monopoly_option, return_center_coord=True)
        if event:
            self.controller.press(event)
            event = self.comparator.template_in_screen(self.check_monopoly_end, return_center_coord=True)
            if event:
                self.controller.press(event)
                event = self.comparator.template_in_screen(self.check_monopoly_end_confirm, return_center_coord=True)
                if event:
                    self.controller.press(event)
                event = self.comparator.template_in_screen(self.check_monopoly_end_confirm, return_center_coord=True)
                if event:
                    self.controller.press(event)

    def back_menu1(self):
        """
        This function is used to back to the main menu.
        
        The function waits until the game is in the game state, if not, it starts the game.
        After that, it waits until the game has the main menu page, if not, it performs
        the operations specified in operate_funcs. The function uses the wait_until
        function to achieve this. If the timeout is reached, it will execute the
        time_out_operate_funcs.
        
        Note: The code for the operations is commented out in the function.
        """
        wait_until(self.controller.in_game, operate_funcs=[self.controller.start_game],check_interval=5)
        wait_until(self._check_have_menu1, operate_funcs=[self.check_in_starting_screen_and_start, self.check_menu2_and_back_menu1, self.check_and_cancel, self.check_monopoly_and_leave], timeout=60, check_interval=1, time_out_operate_funcs=[self.controller.restart_game])