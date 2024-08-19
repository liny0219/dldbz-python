import cv2
import numpy as np

def automatic_background_removal(image_path, output_path):
    # 读取图像
    image = cv2.imread(image_path)
    
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 应用简单的阈值化来检测边缘
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    
    # 由于边缘可能只有1个像素，我们可以稍微膨胀一下以便更好地显示和处理
    kernel = np.ones((3, 3), np.uint8)  # 调整核大小以适应您的图像
    dilated_thresh = cv2.dilate(thresh, kernel, iterations=1)  # 小心调整迭代次数
    
    # 使用阈值化后的图像作为掩膜进行抠图
    result = cv2.bitwise_and(image, image, mask=dilated_thresh)
    
    # 显示结果
    cv2.imshow('Original Image', image)
    cv2.imshow('Threshold', thresh)
    cv2.imshow('Dilated Threshold', dilated_thresh)
    cv2.imshow('Result', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 调用函数进行自动抠图
automatic_background_removal('./refs/world/world_ui.png', 'result_image.jpg')