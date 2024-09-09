

import os
import sys
import cv2
import utils.loger as loger
from utils.image_process import check_image_similarity,  \
    color_match_all, color_match_count, color_in_image, find_target_in_image
from utils.singleton import singleton
import uiautomator2 as u2
import easyocr

reader = easyocr.Reader(['en'])


@singleton
class ComparatorVee:
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

    def _cropped_screenshot(self, leftup_coordinate=None, rightdown_coordinate=None, convert_gray=True, save_path=''):
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
        image = self._cropped_screenshot()
        return color_match_all(image, coordinates_colors)

    def match_color_count(self, coordinates_colors):
        """
        返回匹配的像素点的个数。

        参数:
        - coordinates_colors: 包含坐标和对应颜色的列表，格式为 [(coordinate, expected_color), ...]
        返回:
        - 匹配的像素点的个数
        """
        image = self._cropped_screenshot()
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
        cropped_image = self._cropped_screenshot(leftup_coordinate, rightdown_coordinate, convert_gray=False)
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
        else:
            leftup_coordinate = (0, 0)
            rightdown_coordinate = (self.device.info['displayWidth'], self.device.info['displayHeight'])
        asset_path = self.resource_path(template_path)
        template_gray = self._template_image(asset_path)

        cropped_screenshot_gray = self._cropped_screenshot(leftup_coordinate, rightdown_coordinate, save_path=save_path)

        # image_gray中最符合模板template_gray的区域的左上角, 右下角坐标. 且该区域与模板shape一致.
        target_leftup, target_rightdown = find_target_in_image(template_gray, cropped_screenshot_gray)
        # 第二次裁剪, 为了匹配模板template_gray的shape, 此时twice_cropped_screenshot_gray与template_gray有相同shape, 这之后才可调用比较相似度的函数
        twice_cropped_screenshot_gray = cropped_screenshot_gray[target_leftup[1]                                                                : target_rightdown[1], target_leftup[0]: target_rightdown[0]]

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

    def match_point_color(self, points_with_colors, tolerance=20, debug=0, screenshot=None):
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
            if not all(abs(actual_color[i] - expected_color[i]) <= tolerance for i in range(3)):
                return False
        return True

    def get_num_in_image(self, image_path):
        try:
            result = reader.readtext(image_path)
            return int(result[0][1])
        except ValueError:
            return None


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


comparator_vee = ComparatorVee()
