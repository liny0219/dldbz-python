import uiautomator2 as u2
# import time
import cv2
from utils.image_process import crop_save_img
from engine.device_controller import DeviceController
from engine.comparator import Comparator
from utils.config_loader import config_loader
import time

controller = DeviceController(config_loader.get('adb_port'))
comparator = Comparator(controller)

path = './refs/monopoly/play.png'

save = True
if save:
    leftup_coordinate = [820, 440]
    rightdown_coordinate = [864,464]
    comparator._cropped_screenshot( leftup_coordinate, rightdown_coordinate, convert_gray=False, save_path=path)




# activity = controller.d.app_current().get('activity')
# print(activity)

# act = activity == 'com.epicgames.ue4.GameActivity'

# print(act)

