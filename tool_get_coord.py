from __future__ import annotations
from typing import TYPE_CHECKING
from utils.singleton import singleton
from engine.engine import engine
from utils.stoppable_thread import StoppableThread
from utils.config_loader import cfg_startup
import cv2
if TYPE_CHECKING:
    from app_data import AppData


@singleton
class GetCoord:
    def __init__(self, app_data: AppData):
        self.device = engine.device  # 确保这里正确获取设备实例
        self.img = None
        self.app_data = app_data
        self.update_ui = app_data.update_ui
        self.isClosed = True

    def capture_screen(self):
        self.img = self.device.screenshot(format='opencv')
        return self.img

    def show_coordinates_window(self):
        if not self.isClosed:
            self.update_ui("坐标窗口已经打开", 0)
            return
        thread = StoppableThread(target=self.show_coordinates_window_thread, args=(cfg_startup.get('resolution'),))
        thread.start()

    def show_coordinates_window_thread(self, resolution=None):
        self.isClosed = False
        wnd = "ClickWnd"
        if self.device is None:
            engine.set(self.app_data)
            engine.connect()
            self.device = engine.device
        self.img = self.capture_screen()

        def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                b, g, r = self.img[y, x, :]
                self.update_ui(f"点击坐标: ({x},{y},[{r}, {g}, {b}])", 0)
                # print(f"点击处的BGR颜色值为 ({b}, {g}, {r})")
                cv2.putText(self.img, f"({x},{y})", (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
                cv2.imshow(wnd, self.img)

        cv2.namedWindow(wnd, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(wnd, on_EVENT_LBUTTONDOWN)
        cv2.imshow(wnd, self.img)
        if resolution:
            cv2.resizeWindow(wnd, resolution[0], resolution[1])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        self.isClosed = True
