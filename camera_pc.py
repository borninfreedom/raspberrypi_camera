import time

import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import numpy as np
from PIL import ImageTk, Image

# # 初始化摄像头
cap = cv2.VideoCapture(0)

# 设置最高分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# def init_camera():
#     global cap
#     cap = cv2.VideoCapture(0)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# 在主线程之外启动摄像头初始化
# camera_init_thread = threading.Thread(target=init_camera)
# camera_init_thread.start()

def take_photo(file_path):
    # 读取一帧
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # 水平翻转
    # 检查帧是否成功读取
    if not ret:
        print("无法获取帧")
        return

    # 转换为RGB格式（颜色通道顺序为RGB）
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 使用PIL库保存图像
    image = Image.fromarray(frame)
    image.save(file_path, format='PNG',optimize=True, quality=100)  # 指定保存格式为PNG
    # print(f"照片已保存为 {file_path}")

def get_frame():
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if not ret:
        print("无法获取帧")
        return None
    return frame

def save_photo(file_path, frame):
    # 转换为RGB格式（颜色通道顺序为RGB）
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame)
    image.save(file_path, format='PNG',optimize=True, quality=100)

def capture():
    show_white_frame()
    # root.after(200, lambda: take_photo('my_photo.png'))  # 200毫秒后拍照
    time.sleep(0.2)  # 等待0.2秒，确保白屏显示
    frame = get_frame()  # 获取当前帧
    save_thread = threading.Thread(target=save_photo, args=('my_photo.PNG', frame))
    save_thread.start()
    # take_photo('my_photo.png')
    messagebox.showinfo("提示", "照片已保存")


def show_white_frame():
    white_frame = np.ones((720, 1280, 3), np.uint8) * 255
    # white_frame = cv2.cvtColor(white_frame, cv2.COLOR_BGR2RGB)
    photo = ImageTk.PhotoImage(image=Image.fromarray(white_frame))
    label.config(image=photo)
    label.image = photo
    label.update()

# def show_white_frame():
#     for i in range(256):
#         white_frame = np.ones((1080, 1920, 3), np.uint8) * i
#         photo = ImageTk.PhotoImage(image=Image.fromarray(white_frame))
#         label.config(image=photo)
#         label.image = photo
#         label.update()
#         label.after(5)  # 等待5毫秒，控制动画速度


def update_preview():
    while True:
        ret, frame = cap.read()
        if ret:
            # 转换为RGB格式（颜色通道顺序为RGB）
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)  # 水平翻转
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            label.config(image=photo)
            label.image = photo


# 创建主窗口
root = tk.Tk()
root.title("摄像头拍照")

# 创建预览区域
label = ttk.Label(root)
label.grid(row=0, column=0, columnspan=2, sticky="nsew")  # 使用 "nsew" 来使得控件随窗口大小自适应

# 创建拍照按钮
button = ttk.Button(root, text="拍照", command=capture)
button.grid(row=1, column=0, columnspan=2)

# 设置Grid布局的行列权重，以便自动调整大小
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# 启动预览线程
preview_thread = threading.Thread(target=update_preview)
preview_thread.daemon = True
preview_thread.start()

# 启动主事件循环
root.mainloop()
