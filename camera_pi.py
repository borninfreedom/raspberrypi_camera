#!/usr/bin/python3

# This example is essentially the same as app_capture.py, however here
# we use the Qt signal/slot mechanism to get a callback (capture_done)
# when the capture, that is running asynchronously, is finished.

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QWidget)
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from button_styles import CircularButton


# def post_callback(request):
#     label.setText(''.join(f"{k}: {v}\n" for k, v in request.get_metadata().items()))


picam2 = Picamera2()
# picam2.post_callback = post_callback
picam2.configure(picam2.create_preview_configuration(main={"size": (800, 600)}))

app = QApplication([])


def on_button_clicked():
    circular_button.setEnabled(False)
    cfg = picam2.create_still_configuration()
    picam2.switch_mode_and_capture_file(cfg, "test.jpg", signal_function=qpicamera2.signal_done)


def capture_done(job):
    picam2.wait(job)
    circular_button.setEnabled(True)


qpicamera2 = QGlPicamera2(picam2, width=800, height=600, keep_ar=False)
# button = QPushButton("Click to capture JPEG")
circular_button = CircularButton("")
# circular_button.setFixedSize(60, 60)
# label = QLabel()
window = QWidget()
qpicamera2.done_signal.connect(capture_done)
circular_button.clicked.connect(on_button_clicked)


layout_h = QHBoxLayout()
layout_h.addWidget(qpicamera2)
# layout_v.addStretch(1)
layout_h.addWidget(circular_button,)
window.setWindowTitle("Qt Picamera2 App")
window.resize(1200, 600)
window.setLayout(layout_h)

picam2.start()
window.show()
app.exec()
