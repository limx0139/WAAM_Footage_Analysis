# Attempt optical flow on input numpy array
import cv2
import numpy as np

from Scripts.ROIs import movingROI, staticROI
from Scripts.bitmapFunctions import convertToBitmapExponentialFromLinear


fileName = r'input.avi'


def trackUsingOpticalFlow(fileName : str):
    cap = cv2.VideoCapture(fileName)
    if (cap.isOpened()== False):
        print("Error opening video stream or file")
    p0 = None
    staticROIs = []

    # params for ShiTomasi corner detection
    feature_params = dict( maxCorners = 10,
                        qualityLevel = 0.7,
                        minDistance = 7,
                        blockSize = 7 )

    # Parameters for lucas kanade optical flow
    lk_params = dict( winSize  = (11,11),
                    maxLevel = 7,
                    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.5))

    prevBitmap = None
    
    #TODO use threshholding to find the size of the ROI
    
    ROITracker = movingROI(100, 50)
    # Create a mask image for drawing purposes
    mask = np.zeros((480,640,3), dtype= np.uint8)
    print(mask.shape)
    flag = False

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out0 = cv2.VideoWriter('input1.avi', fourcc, 50.0, (640,480), True)
    out1 = cv2.VideoWriter('ROI.avi', fourcc, 50.0, (400,200), True)
    out2 = cv2.VideoWriter('output.avi', fourcc, 50.0, (640,480), True)
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        # Exponential bitmap is used for computer vision, Linear bitmap is used for display.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bitmapExponential = convertToBitmapExponentialFromLinear(gray).astype(np.uint8)
        bitmapLinear = frame
        out0.write(bitmapLinear)
        # Temperature bitmap is saved as well in case it is needed.
        rgb = bitmapLinear
        # find hotspot
        threshold = 0.8 * 255
        hotspotValue = np.max(bitmapLinear)
        # Optical Flow tracking needs a previous image with identifiable features to track the path of said features. So on finding WAAM has begun, we save the image, calculate the trackable features and advance to the next frame.
        if hotspotValue > threshold and not flag:
            flag = True
            print("Hotspot detected, calculating trackable features")
            p0 = cv2.goodFeaturesToTrack(bitmapExponential, mask = None, **feature_params)
            print("Trackable features calculated: ", p0)
            if p0 is None or len(p0) == 0:
                flag = False

        elif hotspotValue > threshold:
            # calculate optical flow
            print("Calculating optical flow")
            p1, st, err = cv2.calcOpticalFlowPyrLK(prevBitmap, bitmapExponential, p0, None, **lk_params)

            # Select good points
            good_new = p1[st==1]
            good_old = p0[st==1]

            # draw the tracks
            for i,(new,old) in enumerate(zip(good_new,good_old)):
                a,b = new.ravel()
                c,d = old.ravel()
                
                mask = cv2.line(mask, (int(a),int(b)),(int(c),int(d)), (0,255,0), 2)
                rgb = cv2.circle(rgb,(int(a),int(b)),5,(255,0,0),-5)
            p0 = good_new.reshape(-1,1,2)
            if len(p0) == 0:
                flag = False

            else:
                ROIBitmapLinear = ROITracker.getROITemperatureCentered(rgb, int(p0[0][0][0]), int(p0[0][0][1]))
                ROIBitmapLinear =  cv2.resize(ROIBitmapLinear, (400,200), dst=None, fx=None, fy=None, interpolation=cv2.INTER_LINEAR)
                cv2.imshow('ROI', ROIBitmapLinear)
                out1.write(ROIBitmapLinear)
        else:
            flag = False
        print(rgb.shape, mask.shape)
        img = cv2.add(rgb,mask)
        cv2.imshow('frame',img)
        out2.write(img)
        # Press Q to quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('s'):
            if p0 is not None:
                staticROIs.append(staticROI(100,50,(int(p0[0][0][0]), int(p0[0][0][1]))))
            continue
        

        # Now update the previous frame and previous points
        prevBitmap = bitmapExponential.copy()
        
        for i in range(len(staticROIs)):
            resized_image = cv2.resize(staticROIs[i].getROITemperatureCentered(rgb), (400,200), dst=None, fx=None, fy=None, interpolation=cv2.INTER_LINEAR)
            
            cv2.imshow('Static ROI ' + str(i) ,resized_image)
            continue
    out1.release()
    out2.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    trackUsingOpticalFlow(fileName)