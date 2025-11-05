#!/usr/bin/env python3
"""
camera_check.py
----------------
Safely test multiple Raspberry Pi v2 cameras on Jetson Nano — one at a time.
"""

import cv2
import time
import os

def detect_cameras(max_cameras=2):
    """Detect connected CSI cameras."""
    connected = []
    for sensor_id in range(max_cameras):
        gst = (
            f"nvarguscamerasrc sensor-id={sensor_id} ! "
            "video/x-raw(memory:NVMM),width=640,height=480,framerate=30/1 ! "
            "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink"
        )
        cap = cv2.VideoCapture(1)
        if cap.isOpened():
            connected.append(sensor_id)
            cap.release()
    return connected

def test_camera(sensor_id):
    """Preview a single camera feed."""
    print(f"\n🎥 Testing camera sensor-id={sensor_id}...")
    gst = (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        "video/x-raw(memory:NVMM),width=640,height=480,framerate=30/1 ! "
        "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink"
    )

    cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print(f"❌ Failed to open camera {sensor_id}.")
        return

    print(f"✅ Camera {sensor_id} opened. Press ESC to exit preview.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame capture failed.")
            continue
        cv2.imshow(f"Camera {sensor_id}", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Camera {sensor_id} test complete.")

if __name__ == "__main__":
    print("🚀 Jetson Nano Camera Check (Sequential Mode)")
    print("---------------------------------------------")

    os.system("ls /dev/video* || echo 'No /dev/video devices found.'")

    connected_cams = detect_cameras()

    if not connected_cams:
        print("\n❌ No cameras detected.")
    else:
        print(f"\n✅ Detected {len(connected_cams)} camera(s): {connected_cams}")

        for cam_id in connected_cams:
            test_camera(cam_id)
            print(f"🔄 Releasing camera {cam_id} and waiting 2 seconds...")
            time.sleep(2)

        print("\n✅ All connected cameras tested successfully!")
