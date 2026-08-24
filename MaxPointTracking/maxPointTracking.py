import cv2
import numpy as np
import sys


from NotMyScripts.ReadERFXFile import ReadERFXFile
from Scripts.bitmapFunctions import  convertToBitmapLinear, convertToTemp, convertToBitmapExponential
fileName = r'VideoSourceFiles\WAAM\2025-12-17-11-40-22_LWIR1.erfx'

imageArray = ReadERFXFile(fileName)
temperatureArray = convertToTemp(imageArray)
bitmapArray = convertToBitmapLinear(temperatureArray)
# Create some random colors
color = np.random.randint(0,255,(100,3))
mask = np.zeros_like(bitmapArray[0])
flag = False
fourcc = cv2.VideoWriter_fourcc(*'XVID')

out = cv2.VideoWriter('output.avi', fourcc, 50.0, (640,480), False)
for i in range(len(bitmapArray)):

    # find hotspot
    threshold = 600
    hotspotValue = np.max(temperatureArray[i])
    hotspotCoordinates = np.unravel_index(np.argmax(temperatureArray[i]), temperatureArray[i].shape)
    numHotSpots = np.sum(temperatureArray[i] == hotspotValue)
    print(hotspotValue, numHotSpots)
    if hotspotValue > threshold and not flag:
        flag = True
        # apply a bitmask so only printing area is visible
        # ret,thresh1 = cv2.threshold(old_gray, 100, 255, cv2.THRESH_BINARY)
        p0 = hotspotCoordinates
    elif hotspotValue > threshold:
        # find all hotspots
        hotspotsCoordinates = np.argwhere(temperatureArray[i] == hotspotValue)
        # find hotspot minimising distance from previous hotspot
        distances = []
        for j in range(len(hotspotsCoordinates)):
            distances.append(np.linalg.norm(hotspotsCoordinates[j] - p0))
        # print(hotspotsCoordinates, distances)
        closestHotspot = hotspotsCoordinates[np.argmin(distances)]
        p1 = closestHotspot

        print(p1,p0)
        # draw the tracks
        b,a = p1
        d,c = p0
            
        mask = cv2.line(mask, (int(a),int(b)),(int(c),int(d)), color[0].tolist(), 2)
        bitmapArray[i] = cv2.circle(bitmapArray[i],(int(a),int(b)),5,color[0].tolist(),-1)
        p0 = p1
    else:
        flag = False
    img = cv2.add(bitmapArray[i],mask)
    cv2.imshow('bitmap',bitmapArray[i])
    cv2.imshow('frame',img)
    k = cv2.waitKey(1) & 0xff
    if k == 27:
        break
    
    # Now update the previous frame and previous points
    old_gray = bitmapArray[i].copy()
    out.write(img)
    
out.release()
cv2.destroyAllWindows()
