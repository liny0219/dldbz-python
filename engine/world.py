
from engine.u2_device import u2_device
from engine.comparator import comparator
from utils.singleton import singleton
from app_data import app_data


@singleton
class World:
    def __init__(self):
        self.debug = False

    def check_in_world(self, screenshot=None):
        """检查游戏世界中，通过左下角菜单的颜色来判断"""
        if (app_data.thread_stoped()):
            return False
        app_data.update_ui("check-世界中", 'debug')
        if comparator.template_compare(f"./assets/world/world_menu_main.png",  match_threshold=0.8, screenshot=screenshot):
            app_data.update_ui("find-在世界中", 'debug')
            return True
        else:
            return False

    def check_in_achievement_menu(self, screenshot=None):
        """检查成就菜单"""
        if (app_data.thread_stoped()):
            return False
        app_data.update_ui("check-成就菜单", 'debug')
        if comparator.template_compare(f"./assets/world/achievement.png", screenshot=screenshot):
            app_data.update_ui("find-成就菜单", 'debug')
            return True
        else:
            return False

    def check_in_achievement_page(self, screenshot=None):
        """检查成就页面"""
        if (app_data.thread_stoped()):
            return None
        app_data.update_ui("check-成就页面", 'debug')
        crood = comparator.template_compare(f"./assets/world/ads_tag.png",
                                            return_center_coord=True, screenshot=screenshot)
        if crood is not None and len(crood) > 0:
            app_data.update_ui("find-在成就页面", 'debug')
            return crood
        else:
            return None

    def check_game_title(self, screenshot=None):
        """检查游戏开始界面"""
        if (app_data.thread_stoped()):
            return False
        app_data.update_ui("check-游戏开始界面", 'debug')
        if comparator.template_compare(f"./assets/world/game_title.png", screenshot=screenshot):
            app_data.update_ui("find-在游戏开始界面")
            return True
        else:
            return False

    def check_net_state(self, screenshot=None):
        """检查网络状态"""
        if (app_data.thread_stoped()):
            return False
        if comparator.template_compare(f"./assets/world/reconnect.png", screenshot=screenshot):
            app_data.update_ui("find-在重连界面")
            return True
        else:
            return False

    def check_stage(self, screenshot=None):
        if (app_data.thread_stoped()):
            return
        app_data.update_ui("check-小剧场中", 'debug')
        points_with_colors = [
            (696, 330, [146, 123, 79]),
            (634, 350, [156, 133, 83]),
            (331, 351, [155, 132, 82]),
            (278, 340, [141, 119, 70]),
        ]
        if comparator.match_point_color(points_with_colors, 20, screenshot=screenshot):
            app_data.update_ui("find-在小剧场中", 'debug')
            return True
        else:
            return False

    def back_world(self):
        if (app_data.thread_stoped()):
            return
        u2_device.device.click(55, 432)
        app_data.update_ui("返回世界")

    def click_btn_close(self):
        if (app_data.thread_stoped()):
            return
        u2_device.device.click(925, 16)
        app_data.update_ui("点击关闭按钮", 'debug')

    def run_right(self):
        if (app_data.thread_stoped()):
            return
        u2_device.device.swipe(500, 280, 600, 280, 0.05)

    def run_left(self):
        if (app_data.thread_stoped()):
            return
        u2_device.device.swipe(500, 280, 400, 280, 0.05)

    def btn_trim_click(self):
        u2_device.device.click(950, 530)

    def btn_menu_click(self):
        u2_device.device.click(69, 449)

    def btn_menu_achievement_click(self):
        u2_device.device.click(295, 444)


world = World()
