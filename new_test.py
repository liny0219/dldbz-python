import uiautomator2 as u2
# import time
import cv2
from utils.image_process import crop_save_img
from engine.device_controller import DeviceController
from engine.comparator import Comparator
from utils.config_loader import cfg_startup
from utils.status import MATCH_CONFIDENCE


controller = DeviceController(cfg_startup.get('adb_port'))
comparator = Comparator(controller)

path = './new.png'

# leftup_coordinate = [85, 218]
# rightdown_coordinate = [140, 221]
# comparator._cropped_screenshot(leftup_coordinate, rightdown_coordinate, convert_gray=True, save_path=path)


leftup_coordinate = [75, 218]
rightdown_coordinate = [150, 221]
pic = comparator.findTemplate(path,  return_center_coord=True, match_level=MATCH_CONFIDENCE.HIGH)
print(pic)

# activity = controller.d.app_current().get('activity')
# print(activity)

# act = activity == 'com.epicgames.ue4.GameActivity'

# print(act)
