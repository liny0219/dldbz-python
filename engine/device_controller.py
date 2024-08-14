import uiautomator2 as u2
import utils.loger as loger
import time 
from utils.config_loader import config_loader

class DeviceController:
    def __init__(self, adb_port):
        self.adb_port = adb_port
        self.d, self.resolution = self._init_device(adb_port)
        self.rand_press_px = config_loader.get("controller.rand_press_px")
        self.press_duration = config_loader.get("controller.press_duration")
        self.swipe_duration = config_loader.get("controller.swipe_duration")
        self.operate_latency = config_loader.get("controller.operate_latency")
        self.default_sleep_ms = config_loader.get("controller.default_sleep_ms")
        self.initialized = True

    def _init_device(self, adb_port):
        # 连接到设备 (使用 USB 或 Wi-Fi)
        device = u2.connect(adb_port)
        info = device.info
        resolution = (info['displayWidth'], info['displayHeight'])
        loger.log_info(f"设备已连接，分辨率{resolution[0]}x{resolution[1]}")
        return device, resolution

    def sleep_ms(self, T = None):
        if not T:
            T = self.default_sleep_ms
        sleep_time_s = T / 1000.
        time.sleep(sleep_time_s)

    def press(self, coordinate, T = None):
        if not T:
            T = self.press_duration
        if self.d:
            x = coordinate[0]
            y = coordinate[1]
            self.d.long_click(x, y, duration= T / 1000.)
            self.sleep_ms(self.operate_latency)
            loger.log_info(f"已按压位置 ({x}, {y}) 持续 {T} 毫秒")
        else:
            loger.log_error("设备未连接")

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

    def capture_screenshot(self):
        if self.d:
            return self.d.screenshot(format='opencv')
        else:
            loger.log_error("设备未连接")
            return None
        
