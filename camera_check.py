#!/usr/bin/env python3
"""
camera_check.py
----------------
Test only Raspberry Pi Camera 1 (sensor-id=1) on Jetson Nano.
"""

import cv2
import os

def test_camera(sensor_id=1):
    """Preview a single camera feed."""
    print(f"\n🎥 Testing camera sensor-id={sensor_id}...")
    gst = (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        "video/x-raw(memory:NVMM),width=640,height=480,framerate=30/1 ! "
        "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink"
    )

    cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print(f"❌ Failed to open camera {sensor_id}. Make sure CAM1 is connected.")
        return

    print(f"✅ Camera {sensor_id} opened. Press ESC to exit preview.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame capture failed. Is CAM1 connected?")
            break
        cv2.imshow(f"Camera {sensor_id}", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Camera {sensor_id} test complete.")


if __name__ == "__main__":
    print("🚀 Jetson Nano Camera Check — CAM1 Only")
    print("----------------------------------------")

    os.system("ls /dev/video* || echo 'No /dev/video devices found.'")
    test_camera(sensor_id=0)

    print("\n✅ Camera check complete.")
