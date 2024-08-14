from paddleocr import paddleocr,PaddleOCR, draw_ocr
import logging
# ocr = PaddleOCR(use_angle_cls=True, lang='ch')

paddleocr.logging.disable(logging.DEBUG)
import uiautomator2 as u2
# import time
import cv2
import numpy as np





device = u2.connect("127.0.0.1:5555")

info = device.info
print(f'The following is the device info: {info}')
print(f'The resolution is {info['displayWidth']}x{info['displayHeight']}')


img = device.screenshot(format='opencv')
print(f'The shape of the image is {img.shape}')

# cv2.imshow("test", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


# x1,y1 = (1108, 58)
# x2,y2 = (1164, 112)
x1,y1 = (1098,56)
x2,y2 = (1170,540)
# x1,y1 = (1656,80)
# x2,y2 = (1750,812)
subimg = img[y1:y2, x1:x2]
# print(subimg)
cv2.imshow("test", subimg)
cv2.waitKey(0)
cv2.destroyAllWindows()

# laplacian = cv2.Laplacian(subimg, cv2.CV_64F)
# laplacian = cv2.convertScaleAbs(laplacian)
# cv2.imshow("test", laplacian)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
cv2.imwrite('ocrtest.jpg',subimg)
# result = ocr.ocr('ocrtest.jpg', cls=True)
# print(result)

ocr = PaddleOCR(lang='ch')  # need to run only once to download and load model into memory
img_path = 'ocrtest.jpg'
result = ocr.ocr(img_path)
# print(result[0][0][1])
# print(result[0][1][1])
# Hp = int(result[0][0][1][0].replace(',',''))
# Mp = int(result[0][1][1][0].replace(',',''))
# print(f'Hp is {Hp}')
# print(f'Mp is {Mp}')
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        print(line)

# 显示结果
from PIL import Image
result = result[0]
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]
scores = [line[1][1] for line in result]
im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
im_show = Image.fromarray(im_show)
im_show.save('result.jpg')









# from utils.controller import * 
# from utils.comparator import * 

# # cropped_image_path = './refs/cropped_image.png'
# # temp_image_path = './refs/round_ui.png'

# # template_path = './refs/battle.png'
# ctr = DeviceController()
# eyes = Comparator(ctr)

# # img = ctr.capture_screenshot()
# # # eyes.match_picture((1480,914),(1824,1029),template_path)
# # obj = cv2.imread(template_path)

# # result = match_template(img, obj)
# # print(result)
# from skimage.metrics import structural_similarity as ssim

# # ctr.press((1522, 592),100)
# # time.sleep(5)
# # ctr.press((782, 764),100)
# # fig = ctr.capture_screenshot()
# # fig = fig[914:1028,1480:1824]
# # cv2.imwrite('./refs/battle.png',fig)
# # cv2.imshow('test',fig)
# # cv2.waitKey(0)

# import numpy as np
# import matplotlib.pyplot as plt

# from skimage import data
# from skimage.feature import match_template



# def match_pic(img, goal):
#     #转灰度图
#     gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     gray_image = np.squeeze(gray_image)
#     gray_goal = cv2.cvtColor(goal, cv2.COLOR_BGR2GRAY)
#     gray_goal = np.squeeze(gray_goal)
#     #在img中最吻合goal的左上角位置, 记为(x,y)
#     result = match_template(np.squeeze(gray_image), np.squeeze(gray_goal))
#     yx = np.unravel_index(np.argmax(result), result.shape)
#     x, y = yx[::-1] 
#     #基于(x,y)在img中截取与goal相同shape的cropped_img
#     h_goal, w_goal = gray_goal.shape 
#     cropped_img = gray_image[y:y+h_goal, x:x+w_goal]
#     #由于cropped_img和goal已有相同shape, 可以用ssim特征匹配
#     similarity_index = ssim(cropped_img, gray_goal)
#     match_similarity = config_loader.get("comparator.pic_match_similarity")
#     loger.log_info(f'相似度:{similarity_index}')
#     if similarity_index >= match_similarity:
#         return True
#     return False


# import os
# current_path = os.getcwd()
# folder_name = 'refs'
# folder_path = os.path.join(os.getcwd(), folder_name)
# template_path = os.path.join(folder_path, 'battle.png')
# image = ctr.capture_screenshot()
# gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# coin = cv2.imread(template_path)
# gray_coin = cv2.cvtColor(coin, cv2.COLOR_BGR2GRAY)
# cv2.imshow('test', gray_coin)
# cv2.waitKey(0)
# # # 获取文件夹内的所有内容
# # contents = os.listdir(folder_path)

# # print("Folder Contents:", contents)

# # print("Current Working Directory:", current_path)

# find = match_pic(image, coin)
# if find:
#     a = 'yes'
# else:
#     a = 'no'
# result = match_template(np.squeeze(gray_image), np.squeeze(gray_coin))
# ij = np.unravel_index(np.argmax(result), result.shape)
# x, y = ij[::-1]
# print(f'({x},{y})')
# hcoin, wcoin = gray_coin.shape
# print(f'({x+wcoin},{y+hcoin})')
# eyes.match_picture((x,y),(x+wcoin,y+hcoin),template_path)
# fig = plt.figure(figsize=(8, 3))
# ax1 = plt.subplot(1, 3, 1)
# ax2 = plt.subplot(1, 3, 2)
# ax3 = plt.subplot(1, 3, 3, sharex=ax2, sharey=ax2)

# ax1.imshow(gray_coin, cmap=plt.cm.gray)
# ax1.set_axis_off()
# ax1.set_title('template')
# ax1.text(0.5, -0.1, ('We find the template: '+a),
#         transform=ax3.transAxes,  # 使用轴坐标系
#         ha='center',  # 水平居中
#         va='center',  # 垂直居中
#         fontsize=12,  # 字体大小
#         color='black')  # 文字颜色


# ax2.imshow(gray_image, cmap=plt.cm.gray)
# ax2.set_axis_off()
# ax2.set_title('image')
# # highlight matched region
# hcoin, wcoin = gray_coin.shape
# rect = plt.Rectangle((x, y), wcoin, hcoin, edgecolor='r', facecolor='none')
# ax2.add_patch(rect)

# ax3.imshow(result)
# ax3.set_axis_off()
# ax3.set_title('`match_template`\nresult')
# # highlight matched region
# ax3.autoscale(False)
# ax3.plot(x, y, 'o', markeredgecolor='r', markerfacecolor='none', markersize=10)

# plt.show()

# # image = data.coins()

# # cv2.imshow('test', image)
# # cv2.waitKey(0)
# # print(type(image))
# # print(image.shape)
# # coin = image[170:220, 75:130]
# # result = match_template(image, coin)

# # print(result.shape)
# # ij = np.unravel_index(np.argmax(result), result.shape)
# # x, y = ij[::-1]

# # fig = plt.figure(figsize=(8, 3))
# # ax1 = plt.subplot(1, 3, 1)
# # ax2 = plt.subplot(1, 3, 2)
# # ax3 = plt.subplot(1, 3, 3, sharex=ax2, sharey=ax2)

# # ax1.imshow(coin)
# # ax1.set_axis_off()
# # ax1.set_title('template')

# # ax2.imshow(image)
# # ax2.set_axis_off()
# # ax2.set_title('image')
# # # highlight matched region
# # hcoin, wcoin = coin.shape
# # rect = plt.Rectangle((x, y), wcoin, hcoin, edgecolor='r', facecolor='none')
# # ax2.add_patch(rect)

# # ax3.imshow(result)
# # ax3.set_axis_off()
# # ax3.set_title('`match_template`\nresult')
# # # highlight matched region
# # ax3.autoscale(False)
# # ax3.plot(x, y, 'o', markeredgecolor='r', markerfacecolor='none', markersize=10)

# # plt.show()