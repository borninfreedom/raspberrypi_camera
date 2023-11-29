#!/usr/bin/python3

# This example is essentially the same as app_capture.py, however here
# we use the Qt signal/slot mechanism to get a callback (capture_done)
# when the capture, that is running asynchronously, is finished.

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QWidget)
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from button_styles import CircularButton
import numpy as np
import time
import configparser
import os

config_file_path = os.path.expanduser("~/.camera_config")

config = configparser.ConfigParser()

try:
    config.read(config_file_path)
    total_captures = config.getint("General", "total_captures")
except (configparser.NoSectionError, configparser.NoOptionError):
    total_captures = 0

# print(f'total_captures = {total_captures}')
picam2 = Picamera2()
# picam2.post_callback = post_callback
picam2.configure(picam2.create_preview_configuration(main={"size": (800, 600)}))
# print(f'dir(picam2) = {dir(picam2)}')
app = QApplication([])

overlay_black = np.zeros((800, 600, 4), dtype=np.uint8)
overlay_black[:, :] = (0, 0, 0, 255)

overlay_origin = np.zeros((800, 600, 4), dtype=np.uint8)
overlay_origin[:, :] = (0, 0, 0, 0)



def on_button_clicked():
    global total_captures
    circular_button.setEnabled(False)


    qpicamera2.set_overlay(overlay_black)
    cfg = picam2.create_still_configuration(raw={})
    total_captures += 1
    picam2.switch_mode_and_capture_file(cfg, f"DSC_{total_captures:04d}.jpg", signal_function=qpicamera2.signal_done)
    picam2.switch_mode_and_capture_file(cfg, f"DSC_{total_captures:04d}.dng", name="raw",signal_function=qpicamera2.signal_done)
    # time.sleep(0.05)
    # overlay[:, :] = (0, 0, 0, 0)
    # qpicamera2.set_overlay(overlay)

    config["General"] = {"total_captures": str(total_captures)}
    with open(config_file_path, "w") as configfile:
        config.write(configfile)



def capture_done(job):

    picam2.wait(job)

    qpicamera2.set_overlay(overlay_origin)
    circular_button.setEnabled(True)


qpicamera2 = QGlPicamera2(picam2, width=800, height=600, keep_ar=False)
# print(dir(qpicamera2))
# print(f'qpicamera2.size = {qpicamera2.size()}')
circular_button = CircularButton("")

window = QWidget()
qpicamera2.done_signal.connect(capture_done)
circular_button.clicked.connect(on_button_clicked)

layout_h = QHBoxLayout()
layout_h.addWidget(qpicamera2)
layout_h.addWidget(circular_button, )
window.setWindowTitle("Qt Picamera2 App")
window.resize(1200, 600)
window.setLayout(layout_h)

picam2.start()
window.show()
app.exec()
