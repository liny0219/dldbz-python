import cv2
import numpy as np
import utils.loger as loger
from skimage.metrics import structural_similarity as ssim
from skimage.feature import match_template

def crop_save_img(coord1, coord2, path, device):
    img = device.screenshot(format='opencv')
    x1, y1 = coord1
    x2, y2 = coord2
    cropped = img[y1:y2, x1:x2]
    cv2.imwrite(path, cropped)

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

def color_match(image, coordinate, expected_color):
    """
    Checks if the pixel color at a specified coordinate in an image matches the expected color.

    Parameters:
    - image: The input image.
    - coordinate: The coordinates of the pixel to check.
    - expected_color: The expected color of the pixel.

    Returns:
    - True if the pixel color matches the expected color, False otherwise.
    """
    if get_pixel_color(image, coordinate) == expected_color:
        return True
    return False

def color_match_coordinate(image, coordinates_colors):
    """
    返回匹配的像素点的坐标
    
    参数:
    - coordinates_colors: 包含坐标和对应颜色的列表，格式为 [(coordinate, expected_color), ...]

    返回:
    - 所有匹配的像素点的坐标
    """
    coordinates = []
    for coordinate, expected_color in coordinates_colors:
        if color_match(image, coordinate, expected_color):
            coordinates.append(coordinate)
    return coordinates

def color_match_count(image, coordinates_colors):
    """
    返回匹配的像素点的个数
    
    参数:
    - coordinates_colors: 包含坐标和对应颜色的列表，格式为 [(coordinate, expected_color), ...]
    - expected_color::List = [B,G,R]
    - coordinate::Union(Tuple, List) = (x_i, y_i)

    返回:
    - 匹配的像素点的个数
    """
    n = 0
    for coordinate, expected_color in coordinates_colors:
        if color_match(image, coordinate, expected_color):
            n += 1
    return n

def color_match_all(img, coordinates_colors):
    """
    检查所有坐标处的 RGB 颜色是否与预期颜色匹配。

    参数:
    - coordinates_colors: 包含坐标和对应颜色的列表，格式为 [(coordinate, expected_color), ...]
    - expected_color::List = [B,G,R]
    - coordinate::Union(Tuple, List) = (x_i, y_i)

    返回:
    - 如果所有指定的像素点颜色都匹配，则返回 True, 否则返回 False
    """
    for coordinate, expected_color in coordinates_colors:
        if not color_match(img, coordinate, expected_color):
            return False
    return True

def color_in_image(img, expected_color):
    """
    Check if any pixel in the image matches the expected color.

    Parameters:
        img (numpy.ndarray): The input image.
        expected_color (numpy.ndarray): The expected color.

    Returns:
        bool: True if any pixel in the image matches the expected color, False otherwise.
    """
    return np.any(np.all(img == expected_color, axis=-1))

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
    - 返回gray_whole_image中最匹配gray_target_image图像的坐标(左上角坐标,右下角坐标)=>((x1, y1), (x2, y2))
    '''
    match_result       = match_template(gray_whole_image, gray_target_image)
    y, x               = np.unravel_index(np.argmax(match_result), match_result.shape)
    length_y, length_x = gray_target_image.shape 

    return ((x, y),(x + length_x, y + length_y))


def find_target_in_image_k(gray_target_image, gray_whole_image,k=1):
    """
    返回gray_whole_image中最匹配gray_target_image图像的k个坐标

    参数：
    - gray_target_image: 预期匹配的灰度图像。
    - gray_whole_image: 被匹配的灰度图像
    - k: 返回匹配度最高的k个坐标, 默认为1

    返回：
    - 返回gray_whole_image中最匹配gray_target_image图像的k个坐标(左上角坐标,右下角坐标)=>[((x1, y1), (x2, y2))]
    """
    match_result       = match_template(gray_whole_image, gray_target_image)
    top_k_indices = np.argpartition(match_result.flatten(), -k)[-k:]
    top_k_coords = [np.unravel_index(idx, match_result.shape) for idx in top_k_indices]
    length_y, length_x = gray_target_image.shape 
    top_k_coords = [((x, y),(x + length_x, y + length_y)) for y, x in top_k_coords]
    return top_k_coords

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


def match_pic_coord(img, goal):
    #转灰度图
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_image = np.squeeze(gray_image)
    gray_goal = cv2.cvtColor(goal, cv2.COLOR_BGR2GRAY)
    gray_goal = np.squeeze(gray_goal)
    #在img中最吻合goal的左上角位置, 记为(x,y)
    result = match_template(gray_image, gray_goal)
    y, x = np.unravel_index(np.argmax(result), result.shape)
    #基于(x,y)在img中截取与goal相同shape的cropped_img
    h_goal, w_goal = gray_goal.shape 
    cropped_img = gray_image[y:y+h_goal, x:x+w_goal]
    #由于cropped_img和goal已有相同shape, 可以用ssim特征匹配
    similarity_index = ssim(cropped_img, gray_goal)
    if similarity_index >= 0.95:
        return (x, y)
    return None

def match_pic(img, goal):
    #转灰度图
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_image = np.squeeze(gray_image)
    gray_goal = cv2.cvtColor(goal, cv2.COLOR_BGR2GRAY)
    gray_goal = np.squeeze(gray_goal)
    #在img中最吻合goal的左上角位置, 记为(x,y)
    result = match_template(gray_image, gray_goal)
    y,x = np.unravel_index(np.argmax(result), result.shape)
    #基于(x,y)在img中截取与goal相同shape的cropped_img
    h_goal, w_goal = gray_goal.shape 
    cropped_img = gray_image[y:y+h_goal, x:x+w_goal]
    #由于cropped_img和goal已有相同shape, 可以用ssim特征匹配
    similarity_index = ssim(cropped_img, gray_goal)
    if similarity_index >= 0.95:
        return True
    return False

def match_pic_coord_k(img, goal,k=4):
    #转灰度图
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_image = np.squeeze(gray_image)
    gray_goal = cv2.cvtColor(goal, cv2.COLOR_BGR2GRAY)
    gray_goal = np.squeeze(gray_goal)
    #在img中最吻合goal的左上角位置, 记为(x,y)
    match_result       = match_template(gray_image, gray_goal)
    top_k_indices = np.argpartition(match_result.flatten(), -k)[-k:]
    top_k_coords = [np.unravel_index(idx, match_result.shape) for idx in top_k_indices]
    length_y, length_x = gray_goal.shape 
    cropped_imgs = [gray_image[y:y+length_y, x:x+length_x] for (y,x) in top_k_coords]
    #由于cropped_img和goal已有相同shape, 可以用ssim特征匹配
    similarity_indexes = [ssim(cropped_img, gray_goal) for cropped_img in cropped_imgs]
    ret = []
    for index, similarity_index in enumerate(similarity_indexes):
        if similarity_index >= 0.95:
            y,x = top_k_coords[index]
            ret.append((x,y))
    if len(ret) == 0:
        return None
    return ret

def crop_image(image, coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    cropped_image = image[y1:y2, x1:x2]
    return cropped_image
