#!/usr/bin/python3
import time

import numpy as np

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
import cv2

lsize = (320, 240)
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"}, lores={
                                                 "size": lsize, "format": "YUV420"})
picam2.configure(video_config)
picam2.start_preview()
encoder = H264Encoder(1000000, repeat=True)
picam2.start()
picam2.start_encoder(encoder)

w, h = lsize
prev = None
encoding = False
ltime = 0

(rAvg, gAvg, bAvg) = (None, None, None)
total = 0


while True:
    cur = picam2.capture_buffer("lores")
    cur = cur[:w * h * 3 // 2].reshape((int(1.5 * h), w))
    Y = cur[:h, :]
    U = cur[h:h + h // 4, :]
    V = cur[h + h // 4:, :]

    # Ensure all components have the same size
    U = cv2.resize(U, (w, h), interpolation=cv2.INTER_LINEAR)
    V = cv2.resize(V, (w, h), interpolation=cv2.INTER_LINEAR)

    # Merge YUV components to obtain YUV image
    yuv_image = cv2.merge([Y, U, V])

    # Convert YUV to BGR
    bgr_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR_I420)

    # Convert BGR to RGB
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

    (B, G, R) = cv2.split(rgb_image.astype("float"))

    # if the frame averages are None, initialize them
    if rAvg is None:
        rAvg = R
        bAvg = B
        gAvg = G
    # otherwise, compute the weighted average between the history of
    # frames and the current frames
    else:
        rAvg = ((total * rAvg) + (1 * R)) / (total + 1.0)
        gAvg = ((total * gAvg) + (1 * G)) / (total + 1.0)
        bAvg = ((total * bAvg) + (1 * B)) / (total + 1.0)
    # increment the total number of frames read thus far
    total += 1

    if total>10000:break
avg = cv2.merge([bAvg, gAvg, rAvg]).astype("uint8")
cv2.imwrite(args.output, avg)
picam2.stop_encoder()
