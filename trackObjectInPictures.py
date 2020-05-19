#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 07:10:18 2019

@author: kartik (original), john (edits)
"""
import numpy as np
import sys
if  '/opt/ros/kinetic/lib/python2.7/dist-packages' in sys.path : sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2, PIL
from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
#%matplotlib nbagg
import os
import time


## === IMPORTANT ATTRIBUTES ===
marker_side = 0.03

test_name = 'test.csv'

## ============================


def inversePerspective(rvec, tvec):
    R, _ = cv2.Rodrigues(rvec)
    R = np.matrix(R).T
    invTvec = np.dot(-R, np.matrix(tvec))
    invRvec, _ = cv2.Rodrigues(R)
    return invRvec, invTvec


def relativePosition(rvec1, tvec1, rvec2, tvec2):

    rvec1, tvec1 = np.expand_dims(rvec1.squeeze(),1), np.expand_dims(tvec1.squeeze(),1)
    rvec2, tvec2 = np.expand_dims(rvec2.squeeze(),1), np.expand_dims(tvec2.squeeze(),1)
    invRvec, invTvec = inversePerspective(rvec2, tvec2)

    orgRvec, orgTvec = inversePerspective(invRvec, invTvec)

    info = cv2.composeRT(rvec1, tvec1, invRvec, invTvec)
    composedRvec, composedTvec = info[0], info[1]

    composedRvec = composedRvec.reshape((3, 1))
    composedTvec = composedTvec.reshape((3, 1))

    return composedRvec, composedTvec


def estimatePose(frame, marker_side, mtx,dist):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    # detector parameters can be set here (List of detection parameters[3])
    parameters =  aruco.DetectorParameters_create()
    #parameters.adaptiveThreshConstant = 10

    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    if np.all(ids != None):

        # estimate pose of each marker and return the values
        # rvet and tvec-different from camera coefficients
        rvec, tvec = aruco.estimatePoseSingleMarkers(corners, marker_side, mtx, dist)

    return rvec, tvec, corners

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

#mtx = camera intrinsic matrix , dist =  distortion coefficients (k_1, k_2, p_1, p_2[, k_3[, k_4, k_5, k_6]])

if __name__ == "__main__":

    mtx = np.array(((617.0026849655,-0.153855356,315.5900337131),#fx, s,cx
                   (0,614.4461785395,243.0005874753), ##0,fy,cy
                   (0,0,1) ))
    dist = np.array((0.1611730644,-0.3392379107,0.0010744837,	0.000905697)) #k1,k2,p1,p2 ie radial dist and tangential dist

#================ FILE PATH TO IMAGE FOLDER =====================

    path = '/home/john/Documents/research'
    image_folder = '/C'

#================================================================

    frame = cv2.imread(os.path.join(path,image_folder,'left0000.jpg'))

#================================================================

    orig_rvec, orig_tvec, orig_corners = estimatePose(frame,marker_side, mtx, dist)
    orig_corners = orig_corners[0].squeeze()

    total = 0;
    while(True):
        f = []
#        path = '/home/kartik/Boeing/aruco/'
#        image_folder = 'data/camera_images_v6'
        counter = 0;
        for (dirpath, dirnames, filenames) in os.walk(os.path.join(path,image_folder)):
            f.extend(filenames)
            f.sort()
            break


        if len(f) == 0:
            time.sleep(0.5)
            continue
        else:
            for image_ in f:
                if '.ini' in image_:
                    os.remove(os.path.join(path,image_folder,image_))
                    # print('removing'+image_)
                    continue

                #to control processing frequency
#=========++==== CONTROL PROCESSING FREQUENCY HERE ==============
                if np.mod(counter,5) > 0:
#================================================================
                    counter += 1
                    os.remove(os.path.join(path,image_folder,image_))
                    continue

                try:
                    frame = cv2.imread(os.path.join(path,image_folder,image_))
                    next_rvec, next_tvec, next_corners = estimatePose(frame,marker_side, mtx, dist)
                    next_corners = next_corners[0].squeeze()

                    rel_angle  = angle_between(orig_corners[0]-orig_corners[2],next_corners[0]-next_corners[2])

                    rel_rvec, rel_tvec = relativePosition(orig_rvec,orig_tvec, next_rvec,next_tvec)
                    translation = np.round(np.linalg.norm(rel_tvec),4)
                    rotation = rel_angle*180/np.pi
                    rotM = np.zeros(shape=(3,3))
                    cv2.Rodrigues(rel_rvec, rotM, jacobian = 0)
                    ypr = cv2.RQDecomp3x3(rotM)
                except:
                    os.remove(os.path.join(path,image_folder,image_))
                    continue

                os.remove(os.path.join(path,image_folder,image_))

                counter += 1
                total +=1

                rel_pose = np.concatenate((rel_rvec,rel_tvec))
#                point_ = []
#                for i in dst_modified:
##                    for y in i:
#                    point_.append(str(i))

                # point_.append('/n')
                # [point_.append(str(i)) for i in dst_modified]

                #
                file_name = test_name


                with open(os.path.join(path,file_name),'a') as fd:
                # with open('document.csv','wb') as fd:
                    for i in rel_pose:
#                        for y in i:
                        fd.write(str(i[0]))
                        fd.write(',')
                        # print('here')

                    fd.write(str(translation))
                    fd.write(',')
                    fd.write(str(rotation))
                    fd.write('\n')
#                    print(rel_pose)
				print('Completed ' + file_name)
                print('Total: ' + str(total) +' Done '+image_)
