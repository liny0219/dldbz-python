import uiautomator2 as u2
import utils.loger as loger
import time 
from utils.config_loader import config_loader
from utils.load import load_controller_configurations

class DeviceController:
    def __init__(self, adb_port):
        self.adb_port = adb_port
        self.package  = config_loader.get("package")
        self.game_activity = config_loader.get("game_activity")
        self.d, self.resolution = self._init_device(adb_port)
        load_controller_configurations(self)
        self.initialized = True

    def _init_device(self, adb_port):
        device = u2.connect(adb_port)
        info = device.info
        resolution = (info['displayWidth'], info['displayHeight'])
        loger.log_info(f"设备已连接，分辨率{resolution[0]}x{resolution[1]}")
        return device, resolution
    
    def in_game(self):
        if self.d:
            activity = self.d.app_current().get('activity')
            if activity == self.game_activity:
                loger.log_info(f"在游戏")
                return True
            else:
                loger.log_info(f"游戏离线")
                return False
        else:
            loger.log_info(f"游戏离线")
            return False

    def start_game(self):
        if self.d:
            self.d.app_start(self.package)
            loger.log_info(f"开启游戏成功")
            return True
        else:
            loger.log_info(f"开启游戏失败")
            return False
        
    def stop_game(self):
        if self.d:
            self.d.app_stop(self.package)
            loger.log_info(f"关闭游戏成功")
            return True
        else:
            loger.log_info(f"关闭游戏失败")
            return False
    def restart_game(self):
        self.stop_game()
        self.sleep_ms(1000)
        self.start_game()
    def sleep_ms(self, T = None):
        if not T:
            T = self.default_sleep_ms
        sleep_time_s = T / 1000.
        time.sleep(sleep_time_s)

    def press(self, coordinate, T = None, operate_latency=500):
        if not T:
            T = self.press_duration
        if self.d:
            x = coordinate[0]
            y = coordinate[1]
            self.d.long_click(x, y, duration= T / 1000.)
            self.sleep_ms(operate_latency)
            loger.log_info(f"已按压位置 ({x}, {y}) 持续 {T} 毫秒")
        else:
            loger.log_error("设备未连接")

    def light_press(self, coordinate, T = None):
        self.press(coordinate, T = T, operate_latency=100)


    def swipe(self, start_coordinate, end_coordinate, T = None):
        if not T:
            T = self.swipe_duration
        if self.d:
            x_start, y_start = start_coordinate
            x_end, y_end = end_coordinate
            self.d.swipe(x_start, y_start, x_end, y_end, duration=T / 1000.)
            self.sleep_ms(self.operate_latency)
            loger.log_info(f"滑动位置({start_coordinate})到({end_coordinate})持续{T} 毫秒")
        else:
            loger.log_error("设备未连接")

    def light_swipe(self, start_coordinate, end_coordinate, T = None):
        if not T:
            T = self.swipe_duration
        if self.d:
            x_start, y_start = start_coordinate
            x_end, y_end = end_coordinate
            self.d.swipe(x_start, y_start, x_end, y_end, duration=T / 1000.)
            self.sleep_ms(100)
            loger.log_info(f"滑动位置({start_coordinate})到({end_coordinate})持续{T} 毫秒")
        else:
            loger.log_error("设备未连接")

    def capture_screenshot(self):
        if self.d:
            return self.d.screenshot(format='opencv')
        else:
            loger.log_error("设备未连接")
            return None
        
