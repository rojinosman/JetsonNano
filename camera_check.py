#!/usr/bin/env python3
"""
camera_check.py
----------------
Checks and previews Raspberry Pi v2 cameras connected to a Jetson Nano.

Features:
- Lists connected /dev/video* devices
- Tests each camera individually with GStreamer
- Optionally shows both cameras side-by-side in OpenCV
"""

import os
import cv2
import subprocess
import time

def list_video_devices():
    print("🔍 Listing /dev/video* devices:")
    os.system("ls /dev/video* || echo 'No video devices found.'")
    print("\nChecking v4l2 devices:\n")
    os.system("v4l2-ctl --list-devices || echo 'v4l2-ctl not found, install with sudo apt install v4l-utils'")

def test_camera(sensor_id):
    print(f"\n🎥 Testing camera sensor-id={sensor_id} ...")
    gst = (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        "video/x-raw(memory:NVMM),width=640,height=480,framerate=30/1 ! "
        "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink"
    )

    cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print(f"❌ Failed to open camera with sensor-id={sensor_id}.")
        return False

    print(f"✅ Camera {sensor_id} opened successfully. Showing preview (press ESC to exit).")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame grab failed.")
            continue

        cv2.imshow(f"Camera {sensor_id}", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()
    return True


def dual_camera_preview():
    print("\n🎥 Attempting dual camera preview...")
    gst0 = (
        "nvarguscamerasrc sensor-id=0 ! "
        "video/x-raw(memory:NVMM), width=640, height=480, framerate=30/1 ! "
        "nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! appsink"
    )
    gst1 = (
        "nvarguscamerasrc sensor-id=1 ! "
        "video/x-raw(memory:NVMM), width=640, height=480, framerate=30/1 ! "
        "nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! appsink"
    )

    cap0 = cv2.VideoCapture(gst0, cv2.CAP_GSTREAMER)
    cap1 = cv2.VideoCapture(gst1, cv2.CAP_GSTREAMER)

    if not (cap0.isOpened() and cap1.isOpened()):
        print("❌ One or both cameras failed to open. Dual preview not supported on this board.")
        return

    print("✅ Both cameras opened successfully. Press ESC to exit.")
    while True:
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()
        if not (ret0 and ret1):
            print("⚠️ Frame read error.")
            continue

        combined = cv2.hconcat([frame0, frame1])
        cv2.imshow("Dual Camera", combined)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap0.release()
    cap1.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("🚀 Jetson Nano Camera Check Utility")
    print("-----------------------------------")
    list_video_devices()
    time.sleep(1)

    # Test individual cameras
    for cam_id in [0, 1]:
        test_camera(cam_id)

    # Try to show both cameras together
    dual_camera_preview()

    print("\n✅ Camera test completed.")
