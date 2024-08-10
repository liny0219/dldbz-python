import uiautomator2 as u2
import cv2

save = False
# save = True


device = u2.connect("127.0.0.1:16384")

info = device.info
print(f'The following is the device info: {info}')
print(f'The resolution is {info['displayWidth']}x{info['displayHeight']}')


img = device.screenshot(format='opencv')
print(f'The shape of the image is {img.shape}')
if save:
    cv2.imwrite('test.jpg', img)


def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
    global i
    if event == cv2.EVENT_LBUTTONDOWN:
        i+=1
        print(f"The cordination of the {i}-th click is (y={y}, x={x})")
        print(f"The BGR of the {i}-th click is {img[y,x,:]}")
        
        if x>1720:
            cv2.putText(img, f"({y},{x}),{img[y,x,:]}", (x - 200, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (0,0,255), thickness=2)
        elif x<20:
            cv2.putText(img, f"({y},{x}),{img[y,x,:]}", (x + 20, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (0,0,255), thickness=2)
        else:
            cv2.putText(img, f"({y},{x}),{img[y,x,:]}", (x,y), cv2.FONT_HERSHEY_PLAIN, 1.0, (0,0,255), thickness=2)

        cv2.drawMarker(img, (x,y), (255,0,0), cv2.MARKER_STAR, 10,1)



cv2.namedWindow("FindColor", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("FindColor", on_EVENT_LBUTTONDOWN)
i = 0
while True:
    cv2.imshow('FindColor',img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
cv2.destroyAllWindows()



        
