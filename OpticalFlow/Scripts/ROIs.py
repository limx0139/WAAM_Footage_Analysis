# need enough space in array to fit ROI, we fit the point of incidence on the left most side of array, treating it as stationary.
import numpy as np


class movingROI:
    def __init__(self, roiLength, roiHeight):

        self._roiLength = roiLength
        self._roiHeight = roiHeight
        # apparent fixed point of the moving ROI
        self._fixedPoint = [0,0]

    # returns an array for temperature, centered on the fixed point
    def getROITemperatureCentered(self, temperatureArray, fixedPointX, fixedPointY):
        ROI = np.copy(temperatureArray[fixedPointY-self._roiHeight//2:fixedPointY+self._roiHeight//2, fixedPointX-self._roiLength//2:fixedPointX+self._roiLength//2])
        return ROI
    
    def getROITemperatureLeftFitted(self, temperatureArray, fixedPointX, fixedPointY):

        ROI = np.copy(temperatureArray[fixedPointY-self._roiHeight//2:fixedPointY+self._roiHeight//2, fixedPointX:fixedPointX+self._roiLength])
        return ROI

class staticROI:
    def __init__(self, roiLength, roiHeight, fixedPoint):

        self._roiLength = roiLength
        self._roiHeight = roiHeight
        # apparent fixed point of the moving ROI
        self._fixedPoint = fixedPoint

    # returns an array for temperature, centered on the fixed point
    def getROITemperatureCentered(self, temperatureArray):
        fixedPointX, fixedPointY =  self._fixedPoint
        print(self._fixedPoint)
        ROI = np.copy(temperatureArray[fixedPointY-self._roiHeight//2:fixedPointY+self._roiHeight//2, fixedPointX-self._roiLength//2:fixedPointX+self._roiLength//2])
        print(ROI.shape)
        return ROI
    
