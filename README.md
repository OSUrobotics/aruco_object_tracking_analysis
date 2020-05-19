# aruco_object_tracking_analysis
Computer vision analysis for Asterisk Benchmark test. NOTE: this is the penultimate version of the script, need to grab the final version on another computer.

## How to use this
'Videos' of data must be represented as a collection of still frame images. Before running, make sure to set the following attributes, indicated throughout the file.
1. the size of the aruco code (marker_side, units in m)
2. the name of the file generated (test_name)
3. file path to image folder (path, image_folder)
4. control processing frequency (around line 136)

This generates a .csv file with the following attributes:
TODO: add file structure


## Important notes
The aruco tracking analysis script cuts several corners to help with data management.
1. It analyzes every fifth image. You can change this on line 
2. It deletes all of the images after it completes the analysis. MAKE SURE TO HAVE A BACKUP OF YOUR DATA!!
3. I'm a little supersticious. I've tried cleaning up the code and things have stopped working because of it. Haven't had a chance to actually look into it - so I've made some small changes that don't break anything and kept it at that.

## A note on hardware...
We have used this system with two different cameras: a realsense zr300 and a generic logitech webcam.

#### Realsense ZR300
The realsense had its own image saving scripts. 

#### Generic webcam
We wrote our own image saver for generic webcams that follows the same naming image naming conventions as the realsense zr300. See: stream_webcam.py

