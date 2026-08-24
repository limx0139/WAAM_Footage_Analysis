import os

from opticalFlowTracker import trackUsingOpticalFlow

directory = r'C:\Users\kpb26117\OneDrive - University of Strathclyde\Documents\This does not go on Github\Python scripts for ERFX files\VideoSourceFiles\WAAM'

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    path = os.path.join(directory, filename)
    trackUsingOpticalFlow(path)
