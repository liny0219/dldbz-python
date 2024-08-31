import uiautomator2 as u2
import cv2
import numpy as np


def non_max_suppression(boxes, overlapThresh, margin=0):
    if len(boxes) == 0:
        return []
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    pick = []
    x1 = boxes[:, 0] - margin
    y1 = boxes[:, 1] - margin
    x2 = boxes[:, 0] + boxes[:, 2] + margin
    y2 = boxes[:, 1] + boxes[:, 3] + margin
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(x1)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        overlap = (w * h) / area[idxs[:last]]
        overlapping = np.where(overlap > overlapThresh)[0]
        if overlapping.size > 0:
            left_most = np.argmin(x1[idxs[overlapping]])
            pick[-1] = idxs[overlapping][left_most]
        idxs = np.delete(idxs, np.concatenate(([last], overlapping)))
    return boxes[pick].astype("int")


def find_and_draw_matches(device, template_path, region=None, return_center_coords=False, save_path='', custom_threshold=0.8):
    screenshot = device.screenshot(format='opencv')
    # Convert screenshot to grayscale
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    if region:
        x, y, width, height = region
        screenshot_region = gray_screenshot[y:y+height, x:x+width]
    else:
        screenshot_region = gray_screenshot
        x, y = 0, 0

    # Convert template to grayscale
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(screenshot_region, template, cv2.TM_CCOEFF_NORMED)

    loc = np.where(res >= custom_threshold)
    rectangles = [[pt[0] + x, pt[1] + y, w, h] for pt in zip(*loc[::-1])]
    rectangles = np.array(rectangles)
    if len(rectangles):
        rectangles = non_max_suppression(rectangles, 0.3)  # Apply NMS

    result_image = cv2.cvtColor(gray_screenshot, cv2.COLOR_GRAY2BGR)
    if region:
        cv2.rectangle(result_image, (x, y), (x + width, y + height), (255, 0, 0), 3)  # Draw search region in blue

    center_coords = []
    for (x, y, w, h) in rectangles:
        top_left = (x, y)
        bottom_right = (x + w, y + h)
        center_point = (top_left[0] + w//2, top_left[1] + h//2)
        cv2.rectangle(result_image, top_left, bottom_right, (0, 0, 255), 2)
        cv2.circle(result_image, center_point, 2, (0, 255, 255), -1)  # Draw center point in yellow
        center_coords.append(center_point)
        cv2.putText(result_image, f"Top-left: {top_left}",
                    (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(result_image, f"Center: {
                    center_point}", (center_point[0] + 5, center_point[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if return_center_coords:
        return result_image, center_coords
    return result_image


# Connect to the device
d = u2.connect("127.0.0.1:5555")

# Template path
template_path = './new.png'

# Execute template matching and draw results
result_image, match_results = find_and_draw_matches(d, template_path, region=(
    12, 90, 460, 340), return_center_coords=True, custom_threshold=0.8)

# Display results
cv2.imshow('Matched Results', result_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
print(match_results)  # Print the centers
