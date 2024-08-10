import uiautomator2 as u2
import utils.loger as loger
import time 
from utils.config_loader import config_loader

class DeviceController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DeviceController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # 防止重复初始化
            self.d, self.resolution = self._init_device()
            self.rand_press_px = config_loader.get("controller.rand_press_px")
            self.press_duration = config_loader.get("controller.press_duration")
            self.swipe_duration = config_loader.get("controller.swipe_duration")
            self.operate_latency = config_loader.get("controller.operate_latency")
            self.screenshot_path = config_loader.get("controller.screenshot_path")
            self.initialized = True

    def _init_device(self):
        # 连接到设备 (使用 USB 或 Wi-Fi)
        # device = u2.connect(config_loader.get("adb_port"))
        device = u2.connect("127.0.0.1:16384")
        info = device.info
        print(f"Successfully connect a device , the device info is {info}")
        resolution = (info['displayWidth'], info['displayHeight'])
        loger.log_info(f"设备已连接，分辨率{resolution[0]}x{resolution[1]}")
        return device, resolution

    def sleep_ms(self, T):
        sleep_time_s = T / 1000.
        time.sleep(sleep_time_s)

    def press(self, coordinate, T):
        if self.d:
            # coords = self.coordinates(x, y)
            x,y = coordinate
            self.d.long_click(x,y, duration= T / 1000.)
            loger.log_info(f"已按压位置 ({x}, {y}) 持续 {T} 毫秒")
        else:
            loger.log_error("设备未连接")

    def swipe(self, start_coordinate, end_coordinate, T):
        if self.d:
            x_start, y_start = start_coordinate
            x_end, y_end = end_coordinate
            self.d.swipe(x_start, y_start, x_end, y_end, duration=T / 1000.)
            loger.log_info(f"滑动位置({start_coordinate})到({end_coordinate})持续{T} 毫秒")
        else:
            loger.log_error("设备未连接")

    def capture_screenshot(self):
        if self.d:
            return self.d.screenshot(format='opencv')
        else:
            loger.log_error("设备未连接")
            return None
        
