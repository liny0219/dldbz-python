import easyocr
import cv2
from engine.engine import engine_vee

# 初始化 EasyOCR 读者对象
reader = easyocr.Reader(['en'])


# 获取截图 (假设 self.screenshot 是 OpenCV 格式)
screenshot = engine_vee.device.screenshot(format='opencv')

# 定义要提取的区域 (x, y, width, height)
x, y, width, height = 720, 480, 10, 20

# 裁剪特定范围的图像
cropped_image = screenshot[y:y+height, x:x+width]
cv2.imwrite('cropped_image.png', cropped_image)
# 使用 EasyOCR 读取图像并识别文字
result = reader.readtext('cropped_image.png', allowlist='0123456789')

print(result)

# 输出识别结果
for (bbox, text, prob) in result:
    print(f"识别到的文本: {text}，置信度: {prob}")
