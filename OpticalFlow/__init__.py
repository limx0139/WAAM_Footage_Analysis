import numpy as np
import struct
import os
import tqdm
import cv2

#Defines the ReadERFXFile
#Written by Matthew 

#fileName = 'I:\\physics\\Non Project Work\\Python erfx code\\Data\\Current Python scripts\\23.10.2024\\ImagePro LWIR Movies\\Video_30S_36FPS.erfx'

# frameFile = "C://Users/ptb17129/Downloads/test video frame 1.csv"

fileName = r'C:\Users\kpb26117\OneDrive - University of Strathclyde\Documents\This does not go on Github\Python scripts for ERFX files\2025-12-17-13-01-14_LWIR1.erfx'

def ReadERFXFile(filename: str):
    with open(filename, mode='rb') as file:
        commonHeaderSizeBytes = 12
        fileHeader = file.read(commonHeaderSizeBytes)

        #ERF is all little endian
        #Header is all ushort 
        fileHeader = struct.unpack("<6H", fileHeader)

        fileVersion = fileHeader[0]
        productCode = fileHeader[1]
        cameraTypeCode = fileHeader[2]
        imageWidth = fileHeader[3]
        imageHeight = fileHeader[4]
        
        
        headerSizeBytes = commonHeaderSizeBytes

        if fileVersion == 8: 
            versionHeaderSizeBytes = 297
            versionHeader = file.read(versionHeaderSizeBytes)
            frameMetadataSizeBytes = struct.unpack_from("<H", versionHeader, 267)[0]
            fileMetadataOffset = struct.unpack_from("<q", versionHeader, len(versionHeader)-8)[0]            
            #Parse the versionHeader if needed
        elif fileVersion == 7:
            versionHeaderSizeBytes = 279
            versionHeader = file.read(versionHeaderSizeBytes)
            frameMetadataSizeBytes = struct.unpack_from("<H", versionHeader, 249)[0]
            fileMetadataOffset = struct.unpack_from("<q", versionHeader, len(versionHeader)-8)[0]
            #Parse the versionHeader if needed
        else:            
            print("Unsupported ERF file version")
            return
        
                
        headerSizeBytes += versionHeaderSizeBytes
        
        frameSizeBytes = imageWidth * imageHeight * 2
        frameDataSizeBytes = frameSizeBytes + frameMetadataSizeBytes        

        #Calculate fileSize in bytes
        statinfo = os.stat(filename)
        fileSizeBytes = statinfo.st_size
        
        #Get the size of just the frame data
        frameFileSizeBytes = (fileSizeBytes - headerSizeBytes) #subtract the size of the header
        frameFileSizeBytes -= (fileSizeBytes - fileMetadataOffset) #subtract the size of the footer

        #Get the total number of frames in the frame data block
        totalFrames = int(frameFileSizeBytes / frameDataSizeBytes)
        #Sanity check - there should be no remaining bytes
        dataRemain = frameFileSizeBytes % frameDataSizeBytes

        if dataRemain != 0:
            print("File format error")
            return
        
        frameArray =  np.zeros((1,imageHeight,imageWidth),np.uint16)
        frameStack = np.zeros((totalFrames,imageHeight,imageWidth),np.uint16)

        print ("Loading all frames...")
        for i in tqdm.tqdm(range(totalFrames)):
            frameStart = i * frameDataSizeBytes + headerSizeBytes
            file.seek(frameStart)
            file.readinto(frameArray)
            frameStack[i] =frameArray 
        return frameStack
    
def convertToTemp(imageArray):
    return (imageArray -2730)/10

# Use fitted exponential graph to represent bitmap, for more degrees of accuracy at higher temperatures
def convertToBitmapExponential(temperatureArray):
    return np.floor(np.exp((np.log(256)/1000 * temperatureArray))-1).astype(np.uint8)

def convertToBitmapLinear(temperatureArray):
    return np.floor(255/1200 * temperatureArray).astype(np.uint8)

if __name__ == "__main__":
    imageArray = ReadERFXFile(fileName)
    # Convert to celsius
    temperatureArray = convertToTemp(imageArray)
    # convert to bitmap using sigmoid
    bitmapArray = convertToBitmapLinear(temperatureArray)
    # Convert to image
    for bitmap in bitmapArray:
        minValue = np.min(bitmap)
        maxValue = np.max(bitmap)
        print(minValue, maxValue)
        # print(bitmap)
        cv2.imshow('bitmap',bitmap)
        cv2.waitKey(1)
