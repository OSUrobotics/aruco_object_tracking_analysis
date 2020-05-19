#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: john
"""

import cv2

cam = cv2.VideoCapture(0)
img_number = 0

while(1):
	ret, frame = cam.read()

	cv2.imwrite(f"image_num{img_number:04}.jpg", frame)
	print(f"saved image_num{img_number:04}.")

	img_number+= 1

cam.release()

