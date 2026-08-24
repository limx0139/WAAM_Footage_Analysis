
# Attempt optical flow on input numpy array
import cv2
import numpy as np



from NotMyScripts.ReadERFXFile import ReadERFXFile, convertToBitmapExponential, fileName, convertToTemp

fileName = r'VideoSourceFiles\WAAM\2025-12-17-11-34-12_LWIR1.erfx'
imageArray = ReadERFXFile(fileName)
temperatureArray = convertToTemp(imageArray)
bitmapArray = convertToBitmapExponential(temperatureArray)

ret,frame1 = cv2.threshold(bitmapArray[0], 100, 255, cv2.THRESH_BINARY)
prvs = frame1
x,y = frame1.shape
hsv = np.zeros((x,y,3), dtype=np.uint8)
hsv[...,1] = 255


for frame2 in bitmapArray:
    # ret,next = cv2.threshold(frame2, 120, 255, cv2.THRESH_TOZERO)
    next = frame2
    flow = cv2.calcOpticalFlowFarneback(prvs,next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    print(flow.shape)

    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
    hsv[...,0] = ang*180/np.pi/2
    hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
    rgb = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)

    cv2.imshow('frame2',rgb)
    cv2.imshow('orignial',next)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
    elif k == ord('s'):
        cv2.imwrite('opticalfb.png',frame2)
        cv2.imwrite('opticalhsv.png',rgb)
    prvs = next

cv2.destroyAllWindows()


# cv2.cvtColor(grayscale_image, cv2.COLOR_GRAY2RGB)