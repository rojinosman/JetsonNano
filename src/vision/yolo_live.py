#!/usr/bin/env python3
"""
yolo_live.py
Run YOLOv8 object detection on Jetson Nano using CSI camera.
"""

from ultralytics import YOLO
import cv2

# Load model (small = fast)
model = YOLO("yolov8n.pt")

# Jetson Nano CSI camera pipeline
gst = ("nvarguscamerasrc sensor-id=0 ! "  # change 0 → 1 if your camera is on CAM1
       "video/x-raw(memory:NVMM),width=640,height=480,framerate=30/1 ! "
       "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink")


cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("❌ Failed to open camera.")
    exit()

print("✅ YOLOv8 live detection running... (press ESC to exit)")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame capture failed.")
        break

    results = model(frame, verbose=False)
    annotated = results[0].plot()
    cv2.imshow("YOLOv8 - Jetson Nano", annotated)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
