import cv2
import numpy as np
import utils.loger as loger
from skimage.metrics import structural_similarity as ssim
from skimage.feature import match_template

def get_pixel_color(image, coordinate):
    '''
    获得图像指定坐标的像素值。
    
    参数:
    - image: 图像
    - coordinate: 像素的坐标

    返回:
    - 图像在坐标处的像素值
    '''
    x, y = coordinate
    return image[y, x,:]

def colors_matchs(image, coordinates_colors):
    """
    返回匹配的像素点的个数
    
    参数:
    - coordinates_colors: 包含坐标和对应颜色的列表，格式为 [(coordinate, expected_color), ...]

    返回:
    - 匹配的像素点的个数
    """
    results = []
    for coordinate, expected_color in coordinates_colors:
        pixel_color_BGR = get_pixel_color(image, coordinate)
        if pixel_color_BGR == expected_color:
            results.append(coordinate)
    return results


def check_image_similarity(gray_image1, gray_image2, threshold):
    '''
    检测两个图像是否匹配。
    
    参数:
    - gray_image1, gray_image2: 需要比较的灰度图像
    - threshold: 匹配度阈值,大于阈值视为匹配成功

    返回:
    - 如果匹配,返回True;否则返回False
    '''
    similarity_index = ssim(gray_image1, gray_image2)
    loger.log_info(f'相似度:{similarity_index},阈值：{threshold}')
    if similarity_index >= threshold:
        return True
    return False

def find_target_in_image(gray_target_image, gray_whole_image):
    '''
    检查指定区域的图像是否存在指定图像模板。

    参数:
    - gray_target_image: 预期匹配的灰度图像。
    - gray_whole_image: 被匹配的灰度图像

    返回：
    - 返回gray_whole_image中最匹配gray_target_image图像的坐标(左上角坐标,右上角坐标)=>((x1, y1), (x2, y2))
    '''
    match_result       = match_template(gray_whole_image, gray_target_image)
    y, x               = np.unravel_index(np.argmax(match_result), match_result.shape)
    length_y, length_x = gray_target_image.shape 

    return ((x, y),(x + length_x, y + length_y))

def compute_mask(rgba_image):
    """
    计算掩码：从图像的Alpha通道生成掩码。
    
    参数：
        image_path (str): PNG图像的路径。
        
    返回：
        np.ndarray: 生成的掩码。
    """
    
    # 检查图像是否包含Alpha通道
    if rgba_image.shape[2] == 4:
        # 提取Alpha通道
        alpha_channel = rgba_image[:, :, 3]
        
        # 创建掩码：Alpha通道值为0（全透明）的像素设为1，其余设为0
        mask = (alpha_channel == 0).astype(np.uint8)
    else:
        raise ValueError("图像不包含Alpha通道。")
    
    return mask


