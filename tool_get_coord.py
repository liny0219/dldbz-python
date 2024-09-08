import cv2
from utils.singleton import singleton
from engine.engine import engine_vee


@singleton
class GetCoord:
    def __init__(self, update_ui):
        self.device = engine_vee.device  # 确保这里正确获取设备实例
        self.img = None
        self.update_ui = update_ui

    def capture_screen(self):
        self.img = self.device.screenshot(format='opencv')
        return self.img

    def show_coordinates_window(self, resolution=None):
        wnd = "ClickWnd"
        self.img = self.capture_screen()

        def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                b, g, r = self.img[y, x, :]
                self.update_ui(f"点击坐标：({x},{y},[{r}, {g}, {b}])")
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
