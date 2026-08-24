# WAAM Dynamic ROI Implementation

This readme serves as the documentation for the Wire Arc Additive Manufacturing Dynamic Region of Interest software written for AFRC. 

## Authorship

The files contained in folders titled 'NotMyScripts' are not written by me, and ought not to be released to the public as per the owners' request. These scripts are used as helper functions convert the proprietary ERFX files used by AMETEK to save videos in their cameras to bitmap arrays. My image grabber repository (main function in Geometry folder, record temperature data. This feature is admittedly somewhat obscured, I will write a clean script if time permits.) provides a method to record temperature data as AVI files directly, which are readable by cv2.VideoReader, which should make redundant the use of these scripts.

As such, this repository has files redacted and requires the folder 'NotMyScripts' to be present in the same directory as the scripts to run. 

The scripts not contained in folders entitled as such are written myself and are not subject to these restrictions. 


# Contents
 - [Dependencies](#dependencies) 
 - [Scripts](#scripts)
 



## Dependencies

Versions provided are ones used to write the script. Other versions may also work if they are updated. 
| Dependency        | Version | 
| --------          | ------- | 
| Python            | v3.14.6 | 
| struct            |    |
| numpy             | 2.4.6   |
| cv2               | 4.13.0  |
| os                |   |
| tqdm              |      |

```bash
python -m pip install numpy cv2 tqdm
```

## General Notes

The scripts in this repository follow a general methodology:
1. EFRX file is converted to bitmap array format. This is done with the ReadERFXFile.py.
   - 3 copies of the bitmap array are kept:
     - The original temperature array (from 0 to 1050, the temperature range of the LWIR-640 mode used, this is originally in kelvin * 10 and is converted as appropriate.)
       - This is equivalent to the original frames from the camera (without the metadata that is not saved/extracted from the EFRI files), and is the preferred method in saving the data as it is lossless.
     - A linear conversion to uint8 (i.e. 0-255) format (best used for display)
     - An exponential conversion of uint8 format, allowing for more degrees of accuracy for higher temperatures (of which computer vision is more concerned with)
       - This exponential encoding of the data is what is feed in to the tracking algorithms mentioned below as they provide the best and most consistent results, especially for the optical flow algorithm.
2. An algorithm tracking the motion of the welding area (hot area) is implemented by tracking the position of a 'fixed' point on the welding area and stabilising a Region of Interest around this point.
   -  Maximum Point picks the point of maximum temperature as the fixed point
      - This does not work in this case as the maximum temperature of the welding exceeds the maximum measureable temperature of the LWIR-640 Camera Profile, resulting in multiple recorded points of maximum temperature.
      - Regardless, this method may prove useful for its simplicity if the appropriate camera profile, with a high enough temperature range, is used to record future WAAM footage.
   -  Threshold Tracking sets a threshold temperature, controlled by the variable temperatureThreshold, and runs a thresholding operation removing all points of data with temperature below this value. 
      - Needless to say, this uses the temperature bitmap as input data.
      - The threshold area is fitted to a rectangle and the fixed point is set as the center left point of the hot area (This fits the ROI properly for footage for when the welding arm pans right to left but falls short for when it goes left to right, a addition control flow detecting the cardinal motion of the welding arm is to be implemented.)
   - Optical Flow Tracking uses lucas kanade Optical Flow with ShiTomasi Edge detection algorithm to track the motion of a bright point through the video. In most cases, this bright point will be the point of contact of the molten metal deposit into the welding surface.
     - This works the best out of all three options for tracking dynamic ROI, though the fixed point falls off when the welding arm decelerates and stops.
3. Results are displayed and saved as avi format, the input, output and ROI are separately saved.
   - Input data: Raw footage from the ERFX file converted to avi format.
   - Output data: Annotated footage, indicating the location of the fixed point tracked over time.
   - ROI data: The extracted ROI footage.

## Scripts

This directory is organised by the method used to track a moving ROI across the screen. Run the scripts from the directory they are in.

### MaxPointTracking Folder

- The folder MaxPointTracking contains the script maxPointTracking.py, which tracks the motion of the point of maximum temperature across the frames. 
  - If there are multiple points of maximum temperature, this picks an arbitrary maximum temperature as per specifications of numpy.max(), which should be the leftmost, topmost point of maximum temperature. 
  - This caveat and the fact that for the sample footage, the WAAM welding temperature exceeds the maximum accurate temperature of the LWIR-640 causes this method to be inaccurate. Though this may be alleviated with a camera mode with a higher temperature range.
- This script also produces a avi video under output.avi
  - A sample video of what to expect is provided:
<p align="center">
<video width="640" height="480" controls>
  <source src="Documentation/Fixed_Point_WAAM.mp4" type="video/mp4">
</video>
</p>

### ThresholdTracking Folder

- The folder ThresholdTracking contains the scripts thresholdTracking.py and trackAllFiles.py. 
  - This tracks the region of the image that exceeds a threshold temperature,  stabilising this region by assuming the leftmost point in this area is a fixed point.

### OpticalFLow Folder



- The folder OpticalFLow tracks the path of a point of interest in the welding well with optical flow algorithm.
  - An exponential transform on the temperature data is used for the optical flow to provide more data points representing higher temperatures.
  - While this is the best method by far, it is not foolproof as the welding well is chaotic, and a spark flying past the tracked point of interest may be enough to disrupt tracking.
  - The ROI is a 100 by 50 rectangle centered on the point of interest.
  - The 's' key is binded to deploying a static ROI where the current ROI is currently situated, to monitor it cooling down.




| Script                                        | Description | 
| --------                                      | ------- | 
| MaxPointTracking\maxPointTracking.py          | Track the path of the maximum point of the file | 
| ThresholdTracking\thresholdTracking.py        | Track the area of the image with temperature exceeding a threshold   |
| ThresholdTracking\trackAllFiles.py            | Run thresholdTracking for all files in VideoSourceFiles\WAAM   |
| OpticalFlow\opticalFlowAllPoints.py           | Run the optical flow algorithm on all points in the image  |
| OpticalFlow\opticalFlowTracker.py           | Run the optical flow algorithm, tracing the path of a good point in the image, when temperature is detected above 800.  |
| OpticalFlow\trackAllFiles.py                | Run the optical flow algorithm on all files in VideoSourceFiles\WAAM     |
| OpticalFlow\opticalFlowTrackerFromAVI.py    | Run the optical flow algorithm from a specified mp4/avi file. The default is input.avi     |

All above files save video files as input.avi, output.avi and ROI.avi. These converted video files for the input, the output, containing where the region of interest is, and the ROI respectively.

## Arm Motion Tracking

The Script trackObjectMovement.py under the folder tests tracks the motion of the arm. This method is a attempt at improving the tracking by not relying on the chaotic welding well. However, due to the low contrast of the welding arm, the ROI is rather unstable. Perhaps this method would benefit from image stabilisation.