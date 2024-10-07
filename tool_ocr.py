import easyocr
import cv2
from engine.u2_device import u2_device
from engine.comparator import comparator
from gameplay.monopoly.index import Monopoly
from app_data import app_data
from gameplay.monopoly.ocr import ocr_number


def shot():
    u2_device.connect()
    screenshot = u2_device.device.screenshot(format='opencv')
    u2_device.connect()
    # 获取截图 (假设 self.screenshot 是 OpenCV 格式)
    screenshot = u2_device.device.screenshot(format='opencv')

    # 定义要提取的区域 (x, y, width, height)
    x, y, width, height = 720, 480, 10, 20

    # 裁剪特定范围的图像
    cropped_image = screenshot[y:y+height, x:x+width]
    cv2.imwrite('cropped_image.png', cropped_image)
    return cropped_image


def read():
    path = 'debug_images/current_image_20240917_003427_crop.png'
    test_image = cv2.imread(path)
    test_image = comparator.process_image(test_image, 120)
    return test_image


def monopoly():
    path = 'debug_images/current_image_20240917_023028_origin.png'
    test_image = cv2.imread(path)
    comparator.init_ocr()
    ocr_number(test_image, debug=True)


# 初始化 EasyOCR 读者对象
reader = easyocr.Reader(['en'])

# image = shot()
image = monopoly()

# cv2.imwrite('ocr.png', image)
# result = reader.readtext('ocr.png', allowlist='0123456789')

# print(result)

# for (bbox, text, prob) in result:
#     print(f"识别到的文本: {text}，置信度: {prob}")
