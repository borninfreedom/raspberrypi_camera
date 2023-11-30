
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QWidget)

button_size=50
class CircularButton(QPushButton):
    def __init__(self, text, parent=None):
        super(CircularButton, self).__init__(text, parent)
        size = button_size  # Set the size of the button (adjust as needed)
        self.size=size
        self.setMinimumSize(size, size)
        self.setMaximumSize(size, size)
        self.setStyleSheet(f"QPushButton {{ border-radius: {size/2}px; background-color: cyan; }}")
    def mousePressEvent(self, event):
        # Change the button appearance when pressed
        self.setStyleSheet(f"QPushButton {{border-radius: {self.size/2}px;background-color: white; }}")
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        # Restore the original appearance when released
        self.setStyleSheet(f"QPushButton {{border-radius: {self.size/2}px;background-color: cyan; }}")
        super().mouseReleaseEvent(event)