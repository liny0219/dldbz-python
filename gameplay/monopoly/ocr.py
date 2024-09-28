
from datetime import datetime
import os
import traceback
import cv2
from app_data import app_data
from engine.engine import engine
from engine.comparator import comparator


def ocr_number(screenshot, crop_type="left", type="ocr"):
    if screenshot is None:
        return None
    width = screenshot.shape[1]
    crop_img = None
    scale_src = None
    result = process_image(screenshot)

    if not is_number(result):
        crop_src = screenshot
        app_data.update_ui("未识别到距离，裁剪重试")

        if crop_type == "left":
            crop_offset = 0.31
            crop_img = crop_src[:, int(crop_offset * width):]
        else:
            crop_offset = 0.33
            left = int(crop_offset * width)
            right = int((1 - crop_offset) * width)
            crop_img = crop_src[:, left:right]
        result = process_image(crop_img)
        if is_number(result):
            app_data.update_ui("裁剪识别成功")

    if not is_number(result):
        scale_src = screenshot
        app_data.update_ui("未识别到距离，缩小重试")
        offset = 10
        scale_image = cv2.copyMakeBorder(scale_src, offset, offset, offset, offset,
                                         cv2.BORDER_CONSTANT, value=[0, 0, 0])
        result = process_image(scale_image)
        if is_number(result):
            app_data.update_ui("缩小识别成功")

    del crop_img
    del scale_src
    return result


def process_image(current_image, threshold=100):
    result = None
    try:
        if current_image is None or len(current_image) == 0:
            return None
        resized_image = cv2.resize(current_image, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
        image = resized_image
        # 分离图像的 BGR 通道
        if resized_image is None or len(resized_image) == 0:
            return None
        if len(resized_image.shape) == 3:
            b_channel, g_channel, r_channel = cv2.split(resized_image)
            # 对每个通道应用阈值操作
            _, b_thresh = cv2.threshold(b_channel, threshold, 255, cv2.THRESH_BINARY)
            _, g_thresh = cv2.threshold(g_channel, threshold, 255, cv2.THRESH_BINARY)
            _, r_thresh = cv2.threshold(r_channel, threshold, 255, cv2.THRESH_BINARY)
            # 将阈值处理后的通道合并回彩色图像
            threshold_image = cv2.merge([b_thresh, g_thresh, r_thresh])
            image = threshold_image
        if image is None or len(image) == 0:
            return None
        result = comparator.get_num_in_image(image)
    except Exception as e:
        app_data.update_ui(f"process_image异常{e},{traceback.format_exc()}")
    finally:
        del current_image
        del resized_image
        del image
    return result


cache_distance = {}
cache_move = {}


def init_ocr_cache(type):
    image_dir_distance = os.path.join("image", "distance", type)
    image_dir_move = os.path.join("image", "move", type)
    init_distance_cache(image_dir_distance)
    init_move_cache(image_dir_move)


def init_distance_cache(image_dir):
    if not check_directory_exists(image_dir):  # 确保目录存在
        return None
    cache_distance.clear()
    files = sorted(
        [f for f in os.listdir(image_dir) if f.endswith(".png")],
        key=lambda x: int(x.replace(".png", "")),  # 提取文件名前的数字并转换为整数
        reverse=True  # 倒序排列
    )
    for image_name in files:
        image_path = os.path.join(image_dir, image_name)
        # todo 后续改为存储二值化图片,减少每次比较的IO操作
        # image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        # # 二值化，阈值为128，超过的变成255，以下的变成0
        # _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
        # cache[image_name.replace(".png", "")] = binary_image
        cache_distance[image_name.replace(".png", "")] = image_path


def init_move_cache(image_dir):
    if not check_directory_exists(image_dir):  # 确保目录存在
        return None

    files = sorted(
        [f for f in os.listdir(image_dir) if f.endswith(".png")],
        key=lambda x: int(x.replace(".png", "")),  # 提取文件名前的数字并转换为整数
        reverse=True  # 倒序排列
    )
    cache_move.clear()
    for image_name in files:
        image_path = os.path.join(image_dir, image_name)
        # todo 后续改为存储二值化图片,减少每次比较的IO操作
        # image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        # # 二值化，阈值为128，超过的变成255，以下的变成0
        # _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
        # cache[image_name.replace(".png", "")] = binary_image
        cache_move[image_name.replace(".png", "")] = image_path


def match_distance_template_in_directory(screenshot, threshold=0.7):
    if screenshot is None or len(screenshot) == 0:  # 确保截图不为空
        return None
    for key in cache_distance.keys():
        path = cache_distance[key]
        if comparator.template_compare(path, screenshot=screenshot, match_threshold=threshold):
            return int(key)
    return None


def match_move_template_in_directory(screenshot, threshold=0.7):
    if screenshot is None or len(screenshot) == 0:  # 确保截图不为空
        return None
    for key in cache_move.keys():
        path = cache_move[key]
        if comparator.template_compare(path, screenshot=screenshot, match_threshold=threshold):
            return int(key)
    return None


def write_ocr_log(result, current_image, type):
    if is_number(result) or len(current_image) == 0:
        return
    if current_image is None or len(current_image) == 0:
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_path = 'debug_images'
    file_name = f'current_image_{timestamp}_{type}.png'
    os.makedirs(debug_path, exist_ok=True)  # 确保目录存在
    engine.cleanup_large_files(debug_path, 10)  # 清理大于 10 MB 的文件
    cv2.imwrite(os.path.join(debug_path, file_name), current_image)
    return file_name


def is_number(value):
    return isinstance(value, (int, float))


def check_directory_exists(directory_path):
    if os.path.isdir(directory_path):
        print(f"目录存在: {directory_path}")
        return True
    else:
        print(f"目录不存在: {directory_path}")
        return False
