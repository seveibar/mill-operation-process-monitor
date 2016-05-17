# Mill Operation Process Monitor

This repo contains research and code that allow for realtime process analysis
using inexpensive sensor peripherals.

/data/ contains sample code that was run and the data that was obtained from it.
/data/xcarve/test1/ contains a video of a sample run and a script for generating spliced images from it for running computer vision techniques on.
/data/VF1/ contains 2 sample G-Code files: O12345.NC and testProgram1.txt. The WithFeature.csv and WithoutFeature.csv files correspond to the testProgram1 G-Code and shows the acceleration and velocity data. The ComplicatedMachining.csv shows the acceleration and velocity data for the O12345.NC G-Code.

/gcode_parser/ contains code for extrapolating basic movements from G-Code commands and can graph out the XYZ position of the 3-axis vertical mill. The code exists in both C++ and Python with some sample G-Code to test it with.

/notebooks/ contains 2 iPython notebooks that includes sections for running computer vision techniques on a parsed video stream to analyze throughput using [SIFT](https://github.com/seveibar/mill-operation-process-monitor/blob/master/notebooks/SIFT%20Feature%20Detection.ipynb) and [SURF](https://github.com/seveibar/mill-operation-process-monitor/blob/master/notebooks/Computer%20Vision%20Library%20Definitions.ipynb).

The lib.py library contains several functions made for analyzing a parsed video. 

The getSharedKeypoints function compares 2 images and detects common points in the pictures to be used in SURF. The function also takes in a sensitivity value, which is set to 0.5 by default.

The getSharedDescriptors function returns descriptors of features that moved significantly in relation to the rest of the stationary points.

The findPointsWithDescriptors function finds a series of points in an image to use for SURF and creates a set of trained descriptors for each point.

The calculateAxisDescriptors function in the CalibrationScene class determines the axises that will be moving. 

The getAxisProjection takes the orthogonal projection of the axises that will be moving.

