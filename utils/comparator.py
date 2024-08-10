import cv2
import numpy as np
import utils.loger as loger
from skimage.metrics import structural_similarity as ssim
from skimage.feature import match_template
from utils.config_loader import config_loader

class Comparator:
    _instance = None

    def __new__(cls, controller):
        if cls._instance is None:
            cls._instance = super(Comparator, cls).__new__(cls)
            cls._instance._init(controller)
        return cls._instance

    def _init(self, controller):
        if not hasattr(self, 'initialized'):  # 防止重复初始化
            self.controller = controller
            self.initialized = True
            self.match_threshold =  config_loader.get("comparator.pic_match_similarity")

    def all_colors_match(self, coordinates_colors):
        """
        检查所有坐标处的 RGB 颜色是否与预期颜色匹配。

        参数:
        - coordinates_colors: 包含坐标和对应颜色的列表，格式为 [(coordinate, expected_color), ...]
        expected_color::List = [B,G,R]
        coordinate::Union(Tuple, List) = (x_i, y_i)

        返回:
        - 如果所有指定的像素点颜色都匹配，则返回 True, 否则返回 False
        """
        image = self.controller.capture_screenshot()
        result = True 
        for coordinate, expected_color in coordinates_colors:
            pixel_color_BGR = get_pixel_color(image, coordinate)
            if pixel_color_BGR != expected_color:
                result =  False
                break
        return result

    def count_matching_colors(self, coordinates_colors):
        """
        返回匹配的像素点的个数。

        参数:
        - coordinates_colors: 包含坐标和对应颜色的列表，格式为 [(coordinate, expected_color), ...]
        返回:
        - 匹配的像素点的个数
        """
        image = self.controller.capture_screenshot()
        match_count = 0
        for coordinate, expected_color in coordinates_colors:
            pixel_color_BGR = get_pixel_color(image, coordinate)
            if pixel_color_BGR == expected_color:
                match_count += 1
        return match_count

    def any_color_match_in_area(self, leftup_coordinate, rightdown_coordinate, expected_color):
        """
        检查指定区域内是否有像素点与指定颜色匹配。

        参数:
        - leftup_coordinate = (x1, y1): 区域的左上角坐标。
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。
        - expected_color: 预期颜色的 RGB 值。

        返回:
        - 如果区域内有像素点与指定颜色匹配，则返回 True, 否则返回 False
        """
        x1,y1 = leftup_coordinate
        x2,y2 = rightdown_coordinate
        image = self.controller.capture_screenshot()
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                pixel_color_BGR = get_pixel_color(image, (x,y))
                if pixel_color_BGR == expected_color:
                    return True 
        return False 
     
    def match_picture(self, start_coordinate, end_coordinate, template_path):

        image = self.controller.capture_screenshot()
        x1,y1 = start_coordinate#left top
        x2,y2 = end_coordinate#right bottom
        cropped_image = image[y1:y2, x1:x2]

        template = cv2.imread(template_path)
        if template is None:
            loger.log_debug(f"无法读取模板图像: {template_path}")
            return False
        
        gray_image1 = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        gray_image2 = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        return gray_match(gray_image1,gray_image2)

    def find_pic(self, goal):
        img = self.controller.capture_screenshot()
        return match_pic(img, goal, self.match_threshold)


#utils 

def get_pixel_color(img, coordinate):
    x,y = coordinate
    return img[y,x,:]


def my_BGR2GRAY(img):
    return np.squeeze(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))


def gray_match(gray_pic1, gray_pic2, threshold):
    similarity_index = ssim(gray_pic1, gray_pic2)
    loger.log_info(f'相似度:{similarity_index}')
    if similarity_index >= threshold:
        return True
    return False

def match_pic(img, goal, threshold):
    #转灰度图
    gray_image = my_BGR2GRAY(img)
    gray_goal = my_BGR2GRAY(goal)
    #在img中最吻合goal的左上角位置, 记为(x,y)
    result = match_template(np.squeeze(gray_image), np.squeeze(gray_goal))
    yx = np.unravel_index(np.argmax(result), result.shape)
    x, y = yx[::-1] 
    #基于(x,y)在img中截取与goal相同shape的cropped_img
    h_goal, w_goal = gray_goal.shape 
    cropped_img = gray_image[y:y+h_goal, x:x+w_goal]
    #由于cropped_img和goal已有相同shape, 可以用ssim特征匹配
    return gray_match(cropped_img, gray_goal,threshold)