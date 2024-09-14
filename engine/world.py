from __future__ import annotations
from typing import TYPE_CHECKING
from engine.engine import engine
from engine.comparator import comparator
from utils.singleton import singleton
from utils.config_loader import cfg_world,cfg_monopoly
from utils.wait import wait_until,wait_until_img

if TYPE_CHECKING:
    from app_data import AppData


@singleton
class World:
    def __init__(self):
        self.global_data = None
        self.debug = False
        self.load_config()
    def load_config(self):
        self.check_world_ui_refs  = \
            cfg_world.get("check.check_world_ui_refs")
        self.check_menu1_ui_refs  = \
            cfg_world.get("check.check_menu1_ui_refs")   # 检测世界图片1
        self.check_menu2_ui_refs  = \
            cfg_world.get("check.check_menu2_ui_refs")   # 检测世界图片2
        self.check_starting_screen = \
            cfg_world.get('check.check_in_starting_screen')
        self.check_cross1 = \
            cfg_world.get('check.check_cross1')
        self.check_cross2 = \
            cfg_world.get('check.check_cross2')
        self.check_monopoly_option = \
            cfg_monopoly.get('check.check_monopoly_option')
        self.check_monopoly_end = \
            cfg_monopoly.get('check.check_monopoly_end')
        self.check_monopoly_end_confirm = \
            cfg_monopoly.get('check.check_monopoly_end_confirm')
    def set(self, global_data: AppData):
        self.global_data = global_data

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str, type='info'):
        self.global_data and self.global_data.update_ui(msg, type)

    def in_world(self, screenshot=None):
        """检查是否在游戏世界中，通过左下角菜单的颜色来判断"""
        if (self.thread_stoped()):
            return False
        self.update_ui("开始检查是否在世界中", 'debug')
        
        have_menu1 = self._check_have_menu1(screenshot)
        if have_menu1:
            self.update_ui("检查到菜单1", 'debug')
            return True
        else:
            return False

    def click_btn_close(self):
        if (self.thread_stoped()):
            return
        engine.device.click(925, 16)
        self.update_ui("点击关闭按钮", 'debug')

    def check_stage(self, screenshot=None):
        if (self.thread_stoped()):
            return
        self.update_ui("开始检查是否在小剧场中", 'debug')
        points_with_colors = [
            (696, 330, [146, 123, 79]),
            (634, 350, [156, 133, 83]),
            (331, 351, [155, 132, 82]),
            (278, 340, [141, 119, 70]),
        ]
        if comparator.match_point_color(points_with_colors, 20, screenshot=screenshot):
            self.update_ui("检查到在小剧场中", 'debug')
            return True
        else:
            return False

    def back_world(self):
        if (self.thread_stoped()):
            return
        engine.device.click(55, 432)
        self.update_ui("返回世界")

    def _check_have_menu1(self,gray_image):
        return comparator.template_in_image(gray_image, self.check_menu1_ui_refs)
    
    def _check_have_menu2(self,gray_image):
        return comparator.template_in_image(gray_image, self.check_menu2_ui_refs)
    
    def _check_have_menu(self):
        gray_image = comparator._cropped_screenshot()
        have_menu1 = self._check_have_menu1(gray_image)
        have_menu2 = self._check_have_menu2(gray_image)
        return have_menu1 or have_menu2

    def check_in_starting_screen_and_start(self,gray_image):
        in_starting = comparator.template_in_image(gray_image, self.check_starting_screen, return_center_coord=True)
        if in_starting:
            engine.press(in_starting)

    def check_and_cancel1(self,gray_image):
        in_cross1 = comparator.template_in_image(gray_image,self.check_cross1, return_center_coord=True)
        if in_cross1:
            engine.press(in_cross1)

    def check_and_cancel2(self,gray_image):
        in_cross2 = comparator.template_in_image(gray_image,self.check_cross2, return_center_coord=True)
        if in_cross2:
            engine.press(in_cross2)

    def check_and_cancel(self,gray_image):
        self.check_and_cancel1(gray_image)
        self.check_and_cancel2(gray_image)

    def check_menu2_and_back_menu1(self,gray_image):
        in_menu2 = comparator.template_in_image(gray_image,self.check_menu2_ui_refs)
        if in_menu2:
            engine.press([50, 100])

    def check_monopoly_and_leave(self,gray_image):
        event = comparator.template_in_image(gray_image,self.check_monopoly_option, return_center_coord=True)
        if event:
            engine.press(event)
            event = comparator.template_in_picture(self.check_monopoly_end, return_center_coord=True)
            if event:
                engine.press(event)
                event = comparator.template_in_picture(self.check_monopoly_end_confirm, return_center_coord=True)
                if event:
                    engine.press(event)

    def back_menu1(self):
        wait_until(engine.check_in_app, operate_funcs=[engine.start_app],check_interval=5)
        wait_until_img(self._check_have_menu1, 
                       operate_funcs=[  self.check_in_starting_screen_and_start, 
                                        self.check_menu2_and_back_menu1, 
                                        self.check_and_cancel, 
                                        self.check_monopoly_and_leave], 
                        timeout=60, 
                        check_interval=1, 
                        time_out_operate_funcs=[engine.restart_game]
                        )



world = World()
