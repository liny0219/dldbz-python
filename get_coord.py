import cv2


class GetCoord:
    def __init__(self, controller, updateUI):
        self.controller = controller
        self.device = controller.d  # 确保这里正确获取设备实例
        self.img = None
        self.updateUI = updateUI

    def capture_screen(self):
        self.img = self.device.screenshot(format='opencv')
        return self.img

    def show_coordinates_window(self, resolution=None):
        if self.img is None:
            self.img = self.capture_screen()

        def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                b, g, r = self.img[y, x, :]
                self.updateUI(f"点击坐标为 (x={x}, y={y})")
                # print(f"点击处的BGR颜色值为 ({b}, {g}, {r})")
                cv2.putText(self.img, f"({x},{y})", (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
                cv2.imshow('点击获取坐标', self.img)

        cv2.namedWindow("ClickWnd", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("ClickWnd", on_EVENT_LBUTTONDOWN)
        cv2.imshow('ClickWnd', self.img)
        if resolution:
            cv2.resizeWindow("ClickWnd", resolution[0], resolution[1])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
