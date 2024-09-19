

import os
import sys
import cv2
import easyocr
import utils.loger as loger
from utils.image_process import check_image_similarity,  \
    color_match_all, color_match_count, color_in_image, find_target_in_image, crop_image
from utils.singleton import singleton
import uiautomator2 as u2
from PIL import Image

import numpy as np


reader = None


@singleton
class Comparator:
    def __init__(self):
        """
        Initializes a Comparator object.

        Parameters:
        - controller (object): The controller object associated with this Comparator. Defaults to None.

        Returns:
        - None
        """
        self.device: u2.Device = None

    def set_device(self, device):
        self.device = device

    def init_ocr(self):
        global reader
        # reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, model_storage_directory='data/ocr')
        reader = easyocr.Reader(['en'], model_storage_directory='data/ocr')

    def _template_image(self, template_path, convert_gray=True):
        '''
        获取模板图像.

        参数：
        - template_path: 模板图像的地址
        - convert_gray: 是否转化为灰度图
        '''

        color_img = cv2.imread(template_path)
        if color_img is None:
            loger.log_debug(f"无法读取模板图像: {template_path}")

        if convert_gray:
            gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
            return gray_img
        else:
            return color_img
    def _cropped_screenshot(self, 
                            leftup_coordinate=None, 
                            rightdown_coordinate=None, 
                            convert_gray=True, 
                            save_path=''):
        '''
        获取截屏.

        参数：
        - leftup_coordinate = (x1, y1): 区域的左上角坐标。
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。
        - convert_gray: 是否转化为灰度图
        '''

        color_img = self.device.screenshot(format='opencv')
        if (leftup_coordinate and rightdown_coordinate):
            x1, y1 = leftup_coordinate
            x2, y2 = rightdown_coordinate
            color_img = color_img[y1:y2, x1:x2]

        if save_path:
            cv2.imwrite(save_path, color_img)

        if convert_gray:
            gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
            return gray_img
        else:
            return color_img

    def _screenshot_cropped_image(self,  
                                  leftup_coordinate=None, 
                                  rightdown_coordinate=None, 
                                  convert_gray=True, 
                                  save_path=''):
        '''
        获取截屏.

        参数：
        - leftup_coordinate = (x1, y1): 区域的左上角坐标。
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。
        - convert_gray: 是否转化为灰度图
        '''
        return self._cropped_screenshot(leftup_coordinate, 
                                        rightdown_coordinate, 
                                        convert_gray, 
                                        save_path)

    def _cropped_image(self,  leftup_coordinate=None, 
                       rightdown_coordinate=None, convert_gray=True, 
                       save_path='', screenshot=None):
        '''
        获取截屏.

        参数：
        - leftup_coordinate = (x1, y1): 区域的左上角坐标。
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。
        - convert_gray: 是否转化为灰度图
        '''
        color_img = screenshot
        if (leftup_coordinate and rightdown_coordinate):
            x1, y1 = leftup_coordinate
            x2, y2 = rightdown_coordinate
            color_img = color_img[y1:y2, x1:x2]

        if save_path:
            cv2.imwrite(save_path, color_img)

        if convert_gray:
            gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
            return gray_img
        else:
            return color_img

    def match_color_all(self, coordinates_colors):
        """
        检查所有坐标处的 RGB 颜色是否与预期颜色匹配。

        参数:
        - coordinates_colors: 包含坐标和对应颜色的列表，格式为 [(coordinate, expected_color), ...]
        - expected_color::List = [B,G,R]
        - coordinate::Union(Tuple, List) = (x_i, y_i)

        返回:
        - 如果所有指定的像素点颜色都匹配，则返回 True, 否则返回 False
        """
        image = self._screenshot_cropped_image()
        return color_match_all(image, coordinates_colors)

    def match_color_count(self, coordinates_colors):
        """
        返回匹配的像素点的个数。

        参数:
        - coordinates_colors: 包含坐标和对应颜色的列表，格式为 [(coordinate, expected_color), ...]
        返回:
        - 匹配的像素点的个数
        """
        image = self._screenshot_cropped_image()
        return color_match_count(image, coordinates_colors)

    def match_color_any_in_area(self, leftup_coordinate, rightdown_coordinate, expected_color):
        """
        检查指定区域内是否有像素点与指定颜色匹配。

        参数:
        - leftup_coordinate = (x1, y1): 区域的左上角坐标。
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。
        - expected_color: 预期颜色的 BGR 值。

        返回:
        - 如果区域内有像素点与指定颜色匹配，则返回 True, 否则返回 False
        """
        cropped_image = self._screenshot_cropped_image(leftup_coordinate, rightdown_coordinate, convert_gray=False)
        return color_in_image(cropped_image, expected_color)

    def resource_path(slef, relative_path):
        """获取资源的绝对路径，处理打包和非打包两种情况"""
        try:
            # PyInstaller 创建临时文件夹，保存打包的文件
            base_path = sys._MEIPASS
        except Exception:
            # 未打包时使用的目录
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def template_in_picture(self, template_path, coordinate=None,
                            return_center_coord=False, save_path='', match_threshold=0.9):
        '''
        检查指定区域的图像是否存在指定图像模板。
        如果有返回目标坐标

        参数:
        - leftup_coordinate    = (x1, y1): 区域的左上角坐标。默认全屏
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。默认全屏
        - template_path: 预期匹配的图像路径。

        返回：
        - 如果存在指定图像模板，则返回图像模板在指定区域中心点的坐标, 否则返回 None
        '''
        leftup_coordinate = None,
        rightdown_coordinate = None
        if coordinate:
            leftup_coordinate = coordinate[0]
            rightdown_coordinate = coordinate[1]
        # else不用赋值, 解释见调用_screenshot_cropped_image
        # else:
        #     leftup_coordinate = (0, 0)
        #     rightdown_coordinate = (self.device.info['displayWidth'], self.device.info['displayHeight'])
        asset_path = self.resource_path(template_path)
        template_gray = self._template_image(asset_path)

        # 若未指定coordinate, leftup_coordinate与rightdown_coordinate都是None, 
        # 此时_cropped_image对应参数接受None, 则默认截取全屏
        cropped_screenshot_gray = self._screenshot_cropped_image(
            leftup_coordinate, rightdown_coordinate, save_path=save_path)

        # image_gray中最符合模板template_gray的区域的左上角, 右下角坐标. 且该区域与模板shape一致.
        target_leftup, target_rightdown = find_target_in_image(template_gray, cropped_screenshot_gray)
        # 第二次裁剪, 为了匹配模板template_gray的shape, 此时twice_cropped_screenshot_gray与template_gray有相同shape, 这之后才可调用比较相似度的函数
        twice_cropped_screenshot_gray = cropped_screenshot_gray[target_leftup[1]: target_rightdown[1], target_leftup[0]: target_rightdown[0]]

        # 检查是否匹配
        is_match = check_image_similarity(twice_cropped_screenshot_gray, template_gray, match_threshold)

        if not return_center_coord:  # 如果不需要返回目标中心坐标
            return is_match
        else:  # 如果需要返回目标中心坐标
            if not is_match:  # 如果不匹配, 说明没找到图像
                return None
            else:  # 如果匹配
                if leftup_coordinate:  # 如果指定了背景图片, 返回全屏的绝对坐标
                    return get_abs_center_coord(leftup_coordinate, target_leftup, target_rightdown)
                else:  # 如果未指定背景图片, 默认背景图片就是全图, 返回全屏的绝对坐标
                    return get_abs_center_coord((0, 0), target_leftup, target_rightdown)
    def template_in_image(self, 
                          gray_image, 
                          template_path, 
                          leftup_coordinate=None, 
                          rightdown_coordinate=None, 
                          return_center_coord=False,
                          match_threshold=0.95):
        
        if (leftup_coordinate and rightdown_coordinate):
            gray_image = crop_image(gray_image, leftup_coordinate, rightdown_coordinate)
        
        
        template_image = self._template_image(template_path)

        target_leftup, target_rightdown = find_target_in_image(template_image, gray_image)

        gray_image = gray_image[target_leftup[1]: target_rightdown[1], target_leftup[0] : target_rightdown[0]]
        
        
        is_match = check_image_similarity(gray_image, template_image, match_threshold)
        if not return_center_coord:  # 如果不需要返回目标中心坐标
            return is_match
        else:  # 如果需要返回目标中心坐标
            if not is_match:  # 如果不匹配, 说明没找到图像
                return None
            else:  # 如果匹配
                if leftup_coordinate:  # 如果指定了背景图片, 返回全屏的绝对坐标
                    return get_abs_center_coord(leftup_coordinate, target_leftup, target_rightdown)
                else:  # 如果未指定背景图片, 默认背景图片就是全图, 返回全屏的绝对坐标
                    return get_abs_center_coord((0, 0), target_leftup, target_rightdown)

    def template_compare(self, template_path, coordinate=None,
                         return_center_coord=False, save_path='', 
                         match_threshold=0.9, screenshot=None, 
                         pack=True, gray=True):
        '''
        检查指定区域的图像是否存在指定图像模板。
        如果有返回目标坐标

        参数:
        - leftup_coordinate    = (x1, y1): 区域的左上角坐标。默认全屏
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。默认全屏
        - template_path: 预期匹配的图像路径。

        返回：
        - 如果存在指定图像模板，则返回图像模板在指定区域中心点的坐标, 否则返回 None
        '''
        leftup_coordinate = None,
        rightdown_coordinate = None
        if coordinate:
            leftup_coordinate = coordinate[0]
            rightdown_coordinate = coordinate[1]
        # else:
        #     leftup_coordinate = (0, 0)
        #     rightdown_coordinate = (self.device.info['displayWidth'], self.device.info['displayHeight'])
        asset_path = template_path

        if pack:
            asset_path = self.resource_path(template_path)

        template_gray = self._template_image(asset_path)
        # 若未指定coordinate, leftup_coordinate与rightdown_coordinate都是None, 
        # 此时_cropped_image对应参数接受None, 则默认截取全屏
        cropped_screenshot_gray = self._cropped_image(
            leftup_coordinate, rightdown_coordinate, save_path=save_path, screenshot=screenshot)

        # image_gray中最符合模板template_gray的区域的左上角, 右下角坐标. 且该区域与模板shape一致.
        target_leftup, target_rightdown = find_target_in_image(template_gray, cropped_screenshot_gray)

        # print(f"template_path:{template_path} target_leftup: {target_leftup}, target_rightdown: {target_rightdown}")

        # 第二次裁剪, 为了匹配模板template_gray的shape, 此时twice_cropped_screenshot_gray与template_gray有相同shape, 这之后才可调用比较相似度的函数
        twice_cropped_screenshot_gray = cropped_screenshot_gray[target_leftup[1]
            : target_rightdown[1], target_leftup[0]: target_rightdown[0]]

        # 检查是否匹配
        is_match = check_image_similarity(twice_cropped_screenshot_gray, template_gray, match_threshold)

        if not return_center_coord:  # 如果不需要返回目标中心坐标
            return is_match
        else:  # 如果需要返回目标中心坐标
            if not is_match:  # 如果不匹配, 说明没找到图像
                return None
            else:  # 如果匹配
                if coordinate:  # 如果指定了背景图片, 返回全屏的绝对坐标
                    return get_abs_center_coord(leftup_coordinate, target_leftup, target_rightdown)
                else:  # 如果未指定背景图片, 默认背景图片就是全图, 返回全屏的绝对坐标
                    return get_abs_center_coord((0, 0), target_leftup, target_rightdown)

    def match_point_color(self, points_with_colors, tolerance=20, debug=0, screenshot=None, cb=None):
        """检查屏幕上的多个点的颜色是否与期望颜色全部相匹配。
        :param points_with_colors: list of tuples, 每个元组包含坐标(x, y)和期望的RGB颜色列表
        :param tolerance: int, 颜色匹配的容忍度
        :return: bool, 如果所有给定的点的颜色与相应的期望颜色匹配，返回True
        """
        if screenshot is None:
            screenshot = self.device.screenshot(format='opencv')  # 返回的是一个numpy.ndarray对象
        for (x, y, expected_color) in points_with_colors:
            expected_color = tuple(expected_color)  # 将列表转换为元组
            # 在numpy数组中使用[y, x]方式获取颜色，并注意BGR到RGB的转换
            actual_color = screenshot[y, x][::-1]  # 切片[::-1]用于将BGR转换为RGB
            if debug == 1:
                print(f"actual_color: {actual_color}, expected_color: {expected_color}")
            if any(abs(actual_color[i] - expected_color[i]) > tolerance for i in range(3)):
                if debug == 1:
                    print(f"actual_color: {actual_color}, expected_color: {expected_color}")
                    cb(x, y, actual_color, expected_color, tolerance)
            if not all(abs(actual_color[i] - expected_color[i]) <= tolerance for i in range(3)):
                return False
        return True

    def get_num_in_image(self, image_path):
        try:
            result = reader.readtext(image_path, detail=0)
            if len(result) == 1:
                return int(result[0])
            return None
        except ValueError:
            return None

    def replace_color(self, pixel, threshold_value):
        """
        判断像素的 RGB 值并替换颜色。
        如果 RGB 值都小于阈值，返回黑色 [0, 0, 0]，否则返回白色 [255, 255, 255]。
        """
        b, g, r = pixel
        if b < threshold_value and g < threshold_value and r < threshold_value:
            return [0, 0, 0]  # 黑色
        else:
            return [255, 255, 255]  # 白色

    def process_image(self, input_image, threshold_value=100):
        """
        对输入的彩色图像进行遍历，根据阈值替换颜色，输出处理后的图像。
        :param input_image: 输入的彩色图像
        :param threshold_value: 阈值，默认值为 100
        :return: 处理后的图像
        """
        # 获取图像的高度和宽度
        if len(input_image.shape) != 3:
            return
        height, width, _ = input_image.shape

        # 遍历每个像素
        for i in range(height):
            for j in range(width):
                # 获取当前像素的 B, G, R 值
                pixel = input_image[i, j]

                # 使用 replace_color 函数替换颜色
                input_image[i, j] = self.replace_color(pixel, threshold_value)

        scale = 10
        input_image = cv2.copyMakeBorder(input_image, scale, scale, scale, scale,
                                         cv2.BORDER_CONSTANT, value=[0, 0, 0])
        scale = 5
        input_image = cv2.resize(input_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        # 转换为灰度图
        gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
        # 进行抗锯齿处理
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        # 自适应阈值处理，增强对比度
        enhanced_image = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                               cv2.THRESH_BINARY, 11, 2)
        # 尝试二值化增强边缘 (尝试不同阈值)
        _, binary_image = cv2.threshold(enhanced_image, 150, 255, cv2.THRESH_BINARY_INV)
        # 锐化图像，增强边缘清晰度
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])  # 锐化核
        sharpened_image = cv2.filter2D(binary_image, -1, kernel)

        return sharpened_image


def get_abs_center_coord(leftup_coordinate, target_leftup, target_rightdown):
    """
    This function calculates the absolute center coordinates of a target area within a larger image.

    Parameters:
    leftup_coordinate (tuple): The coordinates of the top-left corner of the larger image.
    target_leftup (tuple): The coordinates of the top-left corner of the target area.
    target_rightdown (tuple): The coordinates of the bottom-right corner of the target area.

    Returns:
    tuple: The absolute center coordinates (x, y) of the target area.
    """
    abs_x_center = int(leftup_coordinate[0] + (target_leftup[0] + target_rightdown[0]) // 2)
    abs_y_center = int(leftup_coordinate[1] + (target_leftup[1] + target_rightdown[1]) // 2)
    return (abs_x_center, abs_y_center)


comparator = Comparator()
