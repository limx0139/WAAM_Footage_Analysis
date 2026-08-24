# Editted from https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/


# import the necessary packages
from collections import deque
from imutils.video import VideoStream
from matplotlib import image
from matplotlib.cm import hsv
import numpy as np
import argparse
import cv2
import imutils
import time

from NotMyScripts.ReadERFXFile import ReadERFXFile, convertToBitmapExponential, convertToBitmapLinear, convertToTemp
fileName = r'VideoSourceFiles\WAAM\2025-12-17-11-40-22_LWIR1.erfx'

imageArray = ReadERFXFile(fileName)
temperatureArray = convertToTemp(imageArray)
bitmapExponentialArray = convertToBitmapExponential(temperatureArray)
bitmapLinearArray = convertToBitmapLinear(temperatureArray)



welding = False
ROI_Width = 40
ROI_Height = 20

# keep looping
for i in range(len(bitmapExponentialArray)):
	# grab the current frame
	frame = cv2.cvtColor(bitmapLinearArray[i], cv2.COLOR_GRAY2BGR)
	if frame is None:
		break
	frameMaxValue = np.max(frame)
	frameMaxValueIndex = np.unravel_index(np.argmax(frame, axis=None), frame.shape)
	
	if frameMaxValue > 100:
		welding = True
	else:
		welding = False
  
	if welding:
		blurred = cv2.GaussianBlur(bitmapLinearArray[i], (3, 3), 0)
		mask = blurred[0:180, :]
		# Transform the mask to a bitmap with values between 0 and 255, then threshold it to find the region of interest. Erode and dilate the mask to remove noise.

		minValue = np.min(mask)
		maxValue = np.max(mask)
		# transform the mask to a bitmap with values between 0 and 255, then threshold it to find the region of interest. Erode and dilate the mask to remove noise.
		mask = (mask - minValue) / (maxValue - minValue) * 255
		mask = mask.astype(np.uint8)
		cv2.imshow("mask", mask)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)
		mask = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)[1]
		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts =  cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
		cnt = imutils.grab_contours(cnts)
		# Find the biggest rectangle in the contours, and draw it on the frame. This is the moving arm
		rectangle = None
		rectangleArea = 0
		print("Number of contours found: ", len(cnt))
		if len(cnt) > 0:
			for c in cnt:
				x, y, w, h = cv2.boundingRect(c)
				if w*h > rectangleArea:
					rectangleArea = w*h
					rectangle = (x, y, w, h)
					largestContour = c
			x, y, w, h = rectangle
			# draw contour
			cv2.drawContours(frame, [largestContour], 0, (0, 255, 255), 2)
			# draw the bounding rectangle
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
			# identify and draw the welding arc
			# Rectangle provides width for welding arc, brightest pixel provides height.
			ROI_y = frameMaxValueIndex[0] - ROI_Height//2
			ROI_x = x
			cv2.rectangle(frame, (ROI_x, ROI_y), (ROI_x+ROI_Width, ROI_y+ROI_Height), (255, 0, 0), 2)
			region = cv2.resize(frame[ROI_y:ROI_y+ROI_Height, ROI_x:ROI_x+ROI_Width], (400, 200), interpolation=cv2.INTER_LINEAR)
			cv2.imshow("ROI", region)
	# show the frame to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# close all windows
cv2.destroyAllWindows()