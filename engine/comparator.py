import cv2
import numpy as np
import utils.loger as loger
from utils.config_loader import config_loader
from utils.image_process import get_pixel_color ,check_image_similarity, colors_matchs, find_target_in_image,\
    compute_mask
from utils.status import MATCH_CONFIDENCE
from paddleocr import paddleocr,PaddleOCR, draw_ocr
import logging
#关闭paddleocr的debug信息
paddleocr.logging.disable(logging.DEBUG)

class Comparator:
    def __init__(self, controller = None):
        self.controller = controller
        self.ocr = PaddleOCR(lang='ch')
        self.match_thresholds =  config_loader.get("comparator.pic_match_similaritys")
        self.levels = {MATCH_CONFIDENCE.HIGH:0, MATCH_CONFIDENCE.MID:1, MATCH_CONFIDENCE.LOW:2}
    
    def _template_image(self, template_path, convert_gray = True):
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
    
    def _cropped_screenshot(self, leftup_coordinate = None, rightdown_coordinate = None, convert_gray=True):
        '''
        获取截屏.

        参数：
        - leftup_coordinate = (x1, y1): 区域的左上角坐标。
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。
        - convert_gray: 是否转化为灰度图
        '''

        color_img = self.controller.capture_screenshot()
        if(leftup_coordinate and rightdown_coordinate):
            x1, y1 = leftup_coordinate
            x2, y2 = rightdown_coordinate    
            color_img = color_img[y1:y2, x1:x2]
        if convert_gray:
            gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
            return gray_img
        else:
            return color_img
    
     
    def crop_save_image(self, save_path, leftup_coordinate = None, rightdown_coordinate = None):
        cropped_image = self._cropped_screenshot(leftup_coordinate, rightdown_coordinate, convert_gray=False)
        cv2.imwrite(save_path, cropped_image)

    def match_colors_all(self, coordinates_colors):
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
        matchs = colors_matchs(image, coordinates_colors)
        return len(matchs) == len(coordinates_colors)


    def match_colors_count(self, coordinates_colors):
        """
        返回匹配的像素点的个数。

        参数:
        - coordinates_colors: 包含坐标和对应颜色的列表，格式为 [(coordinate, expected_color), ...]
        返回:
        - 匹配的像素点的个数
        """
        image = self._cropped_screenshot()
        matchs = colors_matchs(image, coordinates_colors)
        return len(matchs)

    def match_colors_any_in_area(self, leftup_coordinate, rightdown_coordinate, expected_color):
        """
        检查指定区域内是否有像素点与指定颜色匹配。

        参数:
        - leftup_coordinate = (x1, y1): 区域的左上角坐标。
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。
        - expected_color: 预期颜色的 RGB 值。

        返回:
        - 如果区域内有像素点与指定颜色匹配，则返回 True, 否则返回 False
        """
        x1, y1 = leftup_coordinate
        x2, y2 = rightdown_coordinate
        image  = self._cropped_screenshot()
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                pixel_color_BGR = get_pixel_color(image, (x,y))
                if pixel_color_BGR == expected_color:
                    return True 
        return False 
     
    def match_template_with_picture(self,template_path, leftup_coordinate, rightdown_coordinate, 
                                    match_level = MATCH_CONFIDENCE.HIGH):
        '''
        检查指定区域的图像是否与指定图像模板匹配。

        参数:
        - leftup_coordinate    = (x1, y1): 区域的左上角坐标。
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。
        - template_path: 预期匹配的图像路径。

        返回：
        - 如果区域与指定图像模板，则返回 True, 否则返回 False
        '''
        template_gray = self._template_image(template_path, convert_gray=True)
        cropped_image_gray = self._cropped_screenshot(leftup_coordinate, rightdown_coordinate, convert_gray=True)



        return check_image_similarity(template_gray, cropped_image_gray, self.match_thresholds[self.levels[match_level]])
        
    
    def template_in_picture(self, template_path, leftup_coordinate=None, rightdown_coordinate=None, 
                            return_abs_coord = True, save_path = '', match_level = MATCH_CONFIDENCE.HIGH):
        '''
        检查指定区域的图像是否存在指定图像模板。

        参数:
        - leftup_coordinate    = (x1, y1): 区域的左上角坐标。
        - rightdown_coordinate = (x2, y2): 区域的右下角坐标。
        - template_path: 预期匹配的图像路径。

        返回：
        - 如果存在指定图像模板，则返回图像模板在指定区域中心点的坐标, 否则返回 None
        '''
        template_gray      = self._template_image(template_path, convert_gray=True)
        image_gray         = self._cropped_screenshot(leftup_coordinate, rightdown_coordinate, convert_gray=True)

        target_leftup, target_rightdown = find_target_in_image(template_gray, image_gray)

        is_match           = check_image_similarity(image_gray[target_leftup[1]: target_rightdown[1], target_leftup[0] : target_rightdown[0]], 
                                                    template_gray, self.match_thresholds[self.levels[match_level]])
        
        if(save_path):
            save_img = self._cropped_screenshot(target_leftup, target_rightdown)
            cv2.imwrite(save_path, save_img)

        if not is_match:
            # 如果不匹配, 说明没找到图像
            return None

        if(return_abs_coord and leftup_coordinate):
            return [ int(leftup_coordinate[0] + (target_leftup[0] + target_rightdown[0]) // 2),
                     int(leftup_coordinate[1] + (target_leftup[1] + target_rightdown[1]) // 2)]
        else:
            return [int((target_leftup[0] + target_rightdown[0]) // 2),
                    int((target_leftup[1] + target_rightdown[1]) // 2)]
                        
        
        
        

