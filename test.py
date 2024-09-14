from gameplay.monopoly import Monopoly1
import uiautomator2 as u2
import cv2
from engine.comparator import comparator
from engine.world import world
# device: u2.Device = u2.connect('127.0.0.1:16384')
# color_img = device.screenshot(format='opencv')
# color_img = comparator._cropped_screenshot()
# print(color_img.shape)
# print(color_img.dtype)
# gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
# print(gray_img.shape)
# print(gray_img.dtype)
# monopoly = Monopoly1()
# monopoly.start()
# world.back_menu1()
fig = comparator._cropped_screenshot()
world.check_monopoly_and_leave(fig)
# comparator.template_in_picture(self.check_monopoly_end, return_center_coord=True)