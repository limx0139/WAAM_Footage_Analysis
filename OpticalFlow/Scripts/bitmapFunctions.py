import numpy as np


def convertToTemp(imageArray):
    return (imageArray -2730)/10

# Use fitted exponential graph to represent bitmap, for more degrees of accuracy at higher temperatures
def convertToBitmapExponentialFromLinear(temperatureArray):
    return np.floor(np.exp((np.log(256)/255 * temperatureArray))-1).astype(np.uint8)

def convertToBitmapLinear(temperatureArray):
    return np.floor(255/1200 * temperatureArray).astype(np.uint8)


def convertToBitmapLinearDynamicAdjustment(temperatureArray):
    minValue = np.min(temperatureArray)
    maxValue = np.max(temperatureArray)
    return np.floor(255/(maxValue - minValue) * (temperatureArray - minValue)).astype(np.uint8)

def convertToBitmapLinearDynamicStaticAdjustment(temperatureArray, minValue, maxValue):
    return np.floor(255/(maxValue - minValue) * (temperatureArray - minValue)).astype(np.uint8)