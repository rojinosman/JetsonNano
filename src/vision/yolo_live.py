#!/usr/bin/env python3
"""
yolo_live.py – YOLOv8-Lite on Jetson Nano (auto-setup)
First run:  converts yolov8n.pt → TensorRT engine (Lite)
Later runs:  uses yolov8n-lite.engine for max FPS
"""

from ultralytics import YOLO
import cv2, os, sys, subprocess, time

ENGINE_PATH = "yolov8n-lite.engine"
PT_PATH = "yolov8n.pt"

# ---------------------------------------------------------------------
# Ensure TensorRT engine exists (build once)
# ---------------------------------------------------------------------
if not os.path.exists(ENGINE_PATH):
    print("⚙️  Exporting YOLOv8-Lite TensorRT engine… this can take a few minutes.")
    if not os.path.exists(PT_PATH):
        print("⬇️  Downloading yolov8n.pt…")
        subprocess.run([sys.executable, "-m", "ultralytics", "download", "yolov8n.pt"], check=False)
        # Fallback: use detect-mode once to auto-download
        if not os.path.exists(PT_PATH):
            from ultralytics import YOLO as Y
            Y("yolov8n.pt")
    subprocess.run(["yolo", "export", f"model={PT_PATH}", "format=engine", "half=True"], check=True)
    os.rename("yolov8n.engine", ENGINE_PATH)
    print("✅ Export complete →", ENGINE_PATH)
else:
    print("✅ Found existing", ENGINE_PATH)

# ---------------------------------------------------------------------
# Load model
# ---------------------------------------------------------------------
model = YOLO(ENGINE_PATH)
print("✅ YOLOv8-Lite ready.")

# Jetson Nano CSI camera pipeline
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

print("🚀 YOLOv8-Lite detection started (ESC to quit).")
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame capture failed.");  time.sleep(0.1);  continue
    results = model(frame, verbose=False)
    annotated = results[0].plot()
    cv2.imshow("YOLOv8-Lite", annotated)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break
cap.release()
cv2.destroyAllWindows()
