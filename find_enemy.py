import uiautomator2 as u2
import cv2
import numpy as np


import numpy as np


def non_max_suppression(boxes, overlapThresh, margin=0):
    if len(boxes) == 0:
        return []
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    # 准备返回的列表
    pick = []

    # 计算扩展后的坐标和面积
    x1 = boxes[:, 0] - margin
    y1 = boxes[:, 1] - margin
    x2 = boxes[:, 0] + boxes[:, 2] + margin
    y2 = boxes[:, 1] + boxes[:, 3] + margin
    area = (x2 - x1 + 1) * (y2 - y1 + 1)

    # 按x1坐标排序
    idxs = np.argsort(x1)

    # 进行NMS处理
    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]

        # 先加入当前最左侧的框
        pick.append(i)

        # 计算当前框与其他框的交叉区域
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        overlap = (w * h) / area[idxs[:last]]

        # 找出与当前框重叠并且靠左的框，保留x最小的
        overlapping = np.where(overlap > overlapThresh)[0]
        if overlapping.size > 0:
            left_most = np.argmin(x1[idxs[overlapping]])
            pick[-1] = idxs[overlapping][left_most]  # 保留最左侧的框

        # 删除处理过的框
        idxs = np.delete(idxs, np.concatenate(([last], overlapping)))

    # 返回过滤后的框列表
    return boxes[pick].astype("int")


def find_and_draw_matches(device, template_path, region=None, threshold=0.8):
    screenshot = device.screenshot(format='opencv')
    if region:
        x, y, width, height = region
        screenshot_region = screenshot[y:y+height, x:x+width]
    else:
        screenshot_region = screenshot
        x, y = 0, 0  # Assume full screen if no region is specified
    template = cv2.imread(template_path)
    w, h = template.shape[1], template.shape[0]
    res = cv2.matchTemplate(screenshot_region, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    rectangles = []
    for pt in zip(*loc[::-1]):
        rectangles.append([pt[0] + x, pt[1] + y, w, h])
    rectangles = np.array(rectangles)
    if len(rectangles):
        rectangles = non_max_suppression(rectangles, 0, 10)  # Adjust this threshold to control overlap
    result_image = screenshot.copy()
    # Draw blue rectangle around the search region
    if region:
        cv2.rectangle(result_image, (x, y), (x + width, y + height), (255, 0, 0), 3)  # Blue rectangle
    for (x, y, w, h) in rectangles:
        top_left = (x, y)
        bottom_right = (x + w, y + h)
        cv2.rectangle(result_image, top_left, bottom_right, (0, 0, 255), 2)  # Red rectangle for matches
        coord_text = f"({top_left[0]}, {top_left[1]})"
        cv2.putText(result_image, coord_text, (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
    return result_image


# Connect to the device
d = u2.connect("127.0.0.1:5555")

# Template path
template_path = './new.png'

# Execute template matching and draw results
result_image = find_and_draw_matches(d, template_path, region=[12, 90, 460, 340], threshold=0.58)

# Display results
cv2.imshow('Matched Results', result_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
