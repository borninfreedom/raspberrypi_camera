#!/usr/bin/python3

# This example is essentially the same as app_capture.py, however here
# we use the Qt signal/slot mechanism to get a callback (capture_done)
# when the capture, that is running asynchronously, is finished.
from libcamera import controls
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QWidget, QMessageBox)
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from button_styles import CircularButton,button_size
import numpy as np
import time
import configparser
import os
import logging
from logging.handlers import RotatingFileHandler


# Set up logging
log_file_path = os.path.expanduser("~/camera_app.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


config_file_path = os.path.expanduser("~/.camera_config")
config = configparser.ConfigParser()


try:
    config.read(config_file_path)
    total_captures = config.getint("General", "total_captures")
    output_folder_num=config.getint("General","output_folder_num")
except (configparser.NoSectionError, configparser.NoOptionError):
    total_captures = 0
    output_folder_num=100

output_folder_path=os.path.expanduser(f"~/图片/{output_folder_num}_DCIM")
os.makedirs(output_folder_path, exist_ok=True)
# output_folder = os.path.expanduser("~/图片/100_DCIM")
# current_folder = 100


# def increment_folder():
#     global current_folder
#     current_folder += 1
#     config["General"]["current_folder"] = str(current_folder)
#
# def get_next_folder():
#
#     if total_captures > 9999:
#         increment_folder()
#         return os.path.join(os.path.expanduser(f"~/图片/{current_folder}_DCIM"))
#     else:
#         return output_folder



# print(f'total_captures = {total_captures}')
picam2 = Picamera2()

preview_width = 800
preview_height = picam2.sensor_resolution[1] * 800 // picam2.sensor_resolution[0]
preview_height -= preview_height % 2
preview_size = (preview_width, preview_height)
# We also want a full FoV raw mode, this gives us the 2x2 binned mode.
raw_size = tuple([v // 2 for v in picam2.camera_properties['PixelArraySize']])

# picam2.post_callback = post_callback
picam2.configure(picam2.create_preview_configuration(main={"size": preview_size},raw={"size": raw_size}))


app = QApplication([])

if 'AfMode' not in picam2.camera_controls:
    QMessageBox.critical(None,"Error","摄像头不支持自动对焦")
    quit()

picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})

overlay_black = np.zeros((800, 600, 4), dtype=np.uint8)
overlay_black[:, :] = (0, 0, 0, 255)

# overlay_origin = np.zeros((800, 600, 4), dtype=np.uint8)
# overlay_origin[:, :] = (0, 0, 0, 0)



def on_button_clicked():
    global total_captures
    global output_folder_num
    global output_folder_path

    circular_button.setEnabled(False)

    # output_folder_path = get_next_folder()
    # os.makedirs(output_folder_path, exist_ok=True)

    qpicamera2.set_overlay(overlay_black)
    cfg = picam2.create_still_configuration(raw={})
    total_captures += 1

    if total_captures>9999:
        total_captures=1
        output_folder_num+=1
        output_folder_path=os.path.expanduser(f"~/图片/{output_folder_num}_DCIM")
        os.makedirs(output_folder_path, exist_ok=True)


    jpg_file=os.path.join(output_folder_path,f"DSC_{total_captures:04d}.jpg")
    dng_file = os.path.join(output_folder_path, f"DSC_{total_captures:04d}.dng")
    # picam2.switch_mode_and_capture_file(cfg,jpg_file , signal_function=qpicamera2.signal_done)

    # TODO: When an object is moving and the image is captured this way, the dng file and the jpg file will not be exactly the same.
    picam2.switch_mode_and_capture_file(cfg, dng_file, name="raw",signal_function=qpicamera2.signal_done)
    picam2.switch_mode_and_capture_file(cfg, jpg_file, signal_function=qpicamera2.signal_done)
    # time.sleep(0.05)
    # overlay[:, :] = (0, 0, 0, 0)
    # qpicamera2.set_overlay(overlay)

    config["General"] = {"total_captures": str(total_captures),
                         "output_folder_num": str(output_folder_num)}
    # config["General"] = {"output_folder_num": str(output_folder_num)}
    with open(config_file_path, "w") as configfile:
        config.write(configfile)



def capture_done(job):

    picam2.wait(job)

    qpicamera2.set_overlay(None)
    circular_button.setEnabled(True)


qpicamera2 = QGlPicamera2(picam2, width=preview_width, height=preview_height, keep_ar=False)
# print(dir(qpicamera2))
# print(f'qpicamera2.size = {qpicamera2.size()}')
circular_button = CircularButton("")

window = QWidget()
qpicamera2.done_signal.connect(capture_done)
circular_button.clicked.connect(on_button_clicked)

layout_h = QHBoxLayout()
layout_h.addWidget(qpicamera2)
layout_h.addWidget(circular_button)
window.setWindowTitle("Qt Picamera2 App")
window.resize(preview_width+button_size, preview_height)
window.setLayout(layout_h)

picam2.start()
window.show()
app.exec()
