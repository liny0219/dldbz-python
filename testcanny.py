import cv2
import numpy as np

# 读取图像
image = cv2.imread('test.png')

# 检查图像是否成功加载
if image is None:
    print("图像加载失败，请检查文件路径。")
    exit()

# 转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 增强对比度
alpha = 2.0  # 对比度控制（大于1增强对比度）
beta = 0     # 亮度控制
contrasted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

# 阈值处理，提取高对比度部分
_, thresh = cv2.threshold(contrasted, 200, 255, cv2.THRESH_BINARY)

# 显示和保存结果
cv2.imshow('Contrasted Image', contrasted)
cv2.imshow('Thresholded Image', thresh)

cv2.imwrite('contrasted_image.png', contrasted)
cv2.imwrite('thresholded_image.png', thresh)

cv2.waitKey(0)
cv2.destroyAllWindows()