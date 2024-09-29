
import gc
import time
from app_data import app_data
from engine.world import world
from engine.u2_device import u2_device

from gameplay.monopoly.check_in_world import check_in_world

from gameplay.monopoly.config import config, set_config
from utils.stoppable_thread import StoppableThread


class Ads():
    def __init__(self):
        self.debug = True
        self.screenshot = None

    def shot(self):
        try:
            app_data.update_ui("-----------开始截图", 'debug')
            if self.screenshot is not None:
                del self.screenshot
                self.screenshot = None
                gc.collect()
            self.screenshot = u2_device.device.screenshot(format='opencv')
            app_data.update_ui("-----------截图完成", 'debug')
            return self.screenshot
        except Exception as e:
            app_data.update_ui(f"截图异常{e}")
            return None

    def start(self):
        try:
            self.shot()
            while not app_data.thread_stoped():
                if not u2_device.check_in_app():
                    app_data.update_ui("当前不在应用内", 'debug')
                    time.sleep(3)
                    continue
                if not u2_device.check_in_game():
                    app_data.update_ui("当前不在游戏内", 'debug')
                    time.sleep(3)
                    continue
                if not check_in_world():
                    app_data.update_ui("当前不在世界地图", 'debug')

                    time.sleep(3)
                    continue
                app_data.update_ui("开始检测广告", 'debug')
                self.check()
                time.sleep(3)
            pass
        except Exception as e:
            self.error_loop(e)
