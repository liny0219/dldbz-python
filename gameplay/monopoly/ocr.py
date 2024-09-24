
from datetime import datetime
import os
import traceback
import cv2
from app_data import app_data
from engine.engine import engine
from engine.comparator import comparator


def ocr_number(screenshot, crop_type="left"):
    if screenshot is None:
        return None
    width = screenshot.shape[1]
    crop_img = None
    scale_src = None
    retry_src = None
    list_img = []
    result = process_image(screenshot)

    if not is_number(result):
        retry_src = screenshot
        write_ocr_log(result, screenshot, 'screenshot')
        result = process_image(retry_src)

    write_ocr_log(result, retry_src, 'retry_src')

    if not is_number(result):
        list_img.append(retry_src)
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

    write_ocr_log(result, crop_img, 'crop_img')

    if not is_number(result):
        list_img.append(crop_img)
        scale_src = screenshot
        app_data.update_ui("未识别到距离，缩小重试")
        offset = 10
        scale_image = cv2.copyMakeBorder(scale_src, offset, offset, offset, offset,
                                         cv2.BORDER_CONSTANT, value=[0, 0, 0])
        write_ocr_log(result, scale_image, '')
        result = process_image(scale_image)
        if is_number(result):
            app_data.update_ui("缩小识别成功")

    write_ocr_log(result, scale_src, 'scale_src')

    if not is_number(result):
        list_img.append(scale_image)
        app_data.update_ui("未识别到距离，预处理重试")
        for i in range(len(list_img)):
            pro_img = list_img[i]
            if (len(pro_img) == 0):
                continue
            process_img = comparator.process_image(pro_img, threshold_value=120)
            result = comparator.get_num_in_image(process_img)
            write_ocr_log(result, process_img, f'process_image_{i}')
            del pro_img
            del process_img
        if is_number(result):
            app_data.update_ui("预处理识别成功")
    del crop_img
    del scale_src
    del retry_src
    del list_img
    return result


def process_image(self, current_image, threshold=100):
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


def write_ocr_log(self, result, current_image, type):
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
