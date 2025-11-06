#!/usr/bin/env python3
"""
yolo11_live.py
Run YOLOv11-Lite object detection on Jetson Nano using the CSI camera.
"""

from ultralytics import YOLO
import cv2

# Load YOLOv11-Lite model (nano lite version)
model = YOLO("yolo11n-lite.pt")

# Jetson Nano CSI camera pipeline
gst = (
    "nvarguscamerasrc sensor-id=0 ! "
    "video/x-raw(memory:NVMM),width=(int)640,height=(int)480,framerate=(fraction)30/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw,format=(string)BGRx ! "
    "videoconvert ! "
    "video/x-raw,format=(string)BGR ! appsink"
)

cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("❌ Failed to open camera.")
    exit()

print("✅ YOLOv11-Lite live detection started (press ESC to quit)")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame capture failed.")
        continue

    results = model(frame, verbose=False)
    annotated = results[0].plot()

    cv2.imshow("YOLOv11-Lite", annotated)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
