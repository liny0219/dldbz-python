import uiautomator2 as u2
# import time
import cv2
from utils.image_process import crop_save_img
from engine.device_controller import DeviceController
from engine.comparator import Comparator
from utils.config_loader import cfg_startup
import time

controller = DeviceController(cfg_startup.get('adb_port'))
comparator = Comparator(controller)

path = './refs/monopoly/fourth_forked_road.png'

save = True
if save:
    leftup_coordinate = [608,358]
    rightdown_coordinate = [660,398]
    comparator._cropped_screenshot( leftup_coordinate, rightdown_coordinate, convert_gray=False, save_path=path)




# activity = controller.d.app_current().get('activity')
# print(activity)

# act = activity == 'com.epicgames.ue4.GameActivity'

# print(act)

