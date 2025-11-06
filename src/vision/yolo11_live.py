#!/usr/bin/env python3
"""
yolo11_live.py – YOLOv11-Lite on Jetson Nano (auto-setup)
First run:  converts yolo11n.pt → TensorRT engine (Lite)
Later runs:  uses yolo11n-lite.engine
"""

from ultralytics import YOLO
import cv2, os, sys, subprocess, time

ENGINE_PATH = "yolo11n-lite.engine"
PT_PATH = "yolo11n.pt"

# ---------------------------------------------------------------------
# Ensure TensorRT engine exists
# ---------------------------------------------------------------------
if not os.path.exists(ENGINE_PATH):
    print("⚙️  Exporting YOLOv11-Lite TensorRT engine… this may take several minutes.")
    if not os.path.exists(PT_PATH):
        print("⬇️  Downloading yolo11n.pt automatically…")
        subprocess.run(["yolo", "predict", f"model={PT_PATH}", "source=0"], check=False)
        if not os.path.exists(PT_PATH):
            from ultralytics import YOLO as Y
            Y("yolo11n.pt")
    subprocess.run(["yolo", "export", f"model={PT_PATH}", "format=engine", "half=True"], check=True)
    os.rename("yolo11n.engine", ENGINE_PATH)
    print("✅ Export complete →", ENGINE_PATH)
else:
    print("✅ Found existing", ENGINE_PATH)

# ---------------------------------------------------------------------
# Load model
# ---------------------------------------------------------------------
model = YOLO(ENGINE_PATH)
print("✅ YOLOv11-Lite ready.")

gst = (
    "nvarguscamerasrc sensor-id=0 ! "
    "video/x-raw(memory:NVMM), width=(int)640, height=(int)480, framerate=(fraction)30/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw, format=(string)BGRx ! "
    "videoconvert ! video/x-raw, format=(string)BGR ! appsink"
)

cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("❌ Failed to open camera.")
    sys.exit(1)

print("🚀 YOLOv11-Lite detection started (ESC to quit).")
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame capture failed.");  time.sleep(0.1);  continue
    results = model(frame, verbose=False)
    annotated = results[0].plot()
    cv2.imshow("YOLOv11-Lite", annotated)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()
