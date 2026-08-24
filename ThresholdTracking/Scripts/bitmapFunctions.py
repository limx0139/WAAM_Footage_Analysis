import numpy as np


def convertToTemp(imageArray):
    return (imageArray -2730)/10

# Use fitted exponential graph to represent bitmap, for more degrees of accuracy at higher temperatures
def convertToBitmapExponential(temperatureArray, minTemp = 0, maxTemp = 1000):
    return np.floor(np.exp((np.log(256)/maxTemp * temperatureArray))-1-minTemp).astype(np.uint8)

def convertToBitmapLinear(temperatureArray, minTemp = 0, maxTemp = 1000):
    return np.floor(255/maxTemp * temperatureArray- minTemp).astype(np.uint8)