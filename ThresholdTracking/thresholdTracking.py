# Use cv2.threshold to find ROI
import cv2
import numpy as np
import sys

from Scripts.bitmapFunctions import  convertToBitmapLinear, convertToTemp, convertToBitmapExponential
from NotMyScripts.ReadERFXFile import ReadERFXFile
from Scripts.ROIs import movingROI

fileName = r'VideoSourceFiles\WAAM\2025-12-17-11-40-22_LWIR1.erfx'





def trackUsingThreshold(fileName : str):
    imageArray = ReadERFXFile(fileName)
    temperatureArray = convertToTemp(imageArray)
    bitmapExponentialArray = convertToBitmapExponential(temperatureArray)
    bitmapLinearArray = convertToBitmapLinear(temperatureArray)

    # the threshold temperature to set regions of interest, temperatures above this value are detected as the region of interest
    temperatureThreshold = 600
    threshold = convertToBitmapExponential(temperatureThreshold)
    ROITracker = movingROI(100, 50)
    fixedPointY = None
    prevROI = None
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    out1 = cv2.VideoWriter('ROI.avi', fourcc, 50.0, (400,200), True)
    out2 = cv2.VideoWriter('output.avi', fourcc, 50.0, (640,480), True)
    for i in range(len(bitmapExponentialArray)):
        rgb = cv2.cvtColor(bitmapLinearArray[i], cv2.COLOR_GRAY2RGB)
        if np.max(bitmapExponentialArray[i]) > threshold:
            ret, thresh = cv2.threshold(bitmapExponentialArray[i], threshold, 255, cv2.THRESH_TOZERO)
            nonZeroIndices = np.argwhere(thresh != 0)
            if len(nonZeroIndices) > 4:
                # the 0th index is the y axis because opencv is annoying
                # Find the location of the top, bottom, left, and right points of the thresholded region, fitted in a rectangle
                min_y_idx = np.argmin(nonZeroIndices[:, 0])
                max_y_idx = np.argmax(nonZeroIndices[:, 0])
                min_x_idx = np.argmin(nonZeroIndices[:, 1])
                max_x_idx = np.argmax(nonZeroIndices[:, 1])
                up = [nonZeroIndices[min_y_idx][1], nonZeroIndices[min_y_idx][0]]  
                down = [up[0], nonZeroIndices[max_y_idx][0]]
                
                left = [nonZeroIndices[min_x_idx][1], nonZeroIndices[min_x_idx][0]]
                right = [nonZeroIndices[max_x_idx][1], left[1]] 
                topLeft = [left[0], up[1]]
                bottomRight = [right[0], down[1]]
                rgb = cv2.rectangle(rgb, topLeft, bottomRight, (0,0,255), 1)
                rgb = cv2.line(rgb, left, right, (255,0,0), 2)
                rgb = cv2.line(rgb, up, down, (0,255,0), 2)
                
                # calculate fixed points

                fixedPointY = np.argmax(temperatureArray[i][:,left[0]])
                fixedPointX = left[0]
                rgb = cv2.circle(rgb,(fixedPointX,fixedPointY),5,(255,0,0),-1)
                ROIBitmap = ROITracker.getROITemperatureLeftFitted(rgb, fixedPointX-20, fixedPointY)
                #ROIBitmap = convertToBitmapLinear(ROITemperature)
                ROIBitmap = cv2.resize(ROIBitmap, (400,200), dst=None, fx=None, fy=None, interpolation=cv2.INTER_LINEAR)
                cv2.imshow('ROI', ROIBitmap)
                out1.write(ROIBitmap)
        

        out2.write(rgb)
        cv2.imshow('bitmap',rgb)
        
        # Press Q to quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        continue
    out1.release()
    out2.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    print(fileName)
    trackUsingThreshold(fileName)