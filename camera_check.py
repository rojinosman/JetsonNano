#!/usr/bin/env python3
"""
camera_check.py
----------------
Detects and tests Raspberry Pi v2 cameras connected to a Jetson Nano.

Features:
- Detects how many CSI cameras are connected
- Tests each connected camera using GStreamer + OpenCV
- Handles one or two cameras gracefully
- Shows live preview (press ESC to exit)
"""

import os
import cv2
import time
import subprocess

def detect_cameras(max_cameras=2):
    """
    Detect how many CSI cameras are connected (0, 1, or 2).
    Returns a list of working camera sensor IDs.
    """
    connected = []
    for sensor_id in range(max_cameras):
        gst = (
            f"nvarguscamerasrc sensor-id={sensor_id} ! "
            "video/x-raw(memory:NVMM),width=640,height=480,framerate=30/1 ! "
            "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink"
        )
        cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
        if cap.isOpened():
            connected.append(sensor_id)
            cap.release()
    return connected


def test_camera(sensor_id):
    """Show live preview for a specific camera."""
    print(f"\n🎥 Testing camera sensor-id={sensor_id} ...")
    gst = (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        "video/x-raw(memory:NVMM),width=640,height=480,framerate=30/1 ! "
        "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink"
    )

    cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print(f"❌ Failed to open camera {sensor_id}.")
        return False

    print(f"✅ Camera {sensor_id} opened successfully. Press ESC to exit preview.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame capture failed.")
            continue
        cv2.imshow(f"Camera {sensor_id}", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    return True


def dual_camera_preview():
    """Attempt to open both cameras side-by-side if both are connected."""
    print("\n🎥 Attempting dual camera preview...")

    gst0 = (
        "nvarguscamerasrc sensor-id=0 ! "
        "video/x-raw(memory:NVMM),width=640,height=480,framerate=30/1 ! "
        "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink"
    )
    gst1 = (
        "nvarguscamerasrc sensor-id=1 ! "
        "video/x-raw(memory:NVMM),width=640,height=480,framerate=30/1 ! "
        "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink"
    )

    cap0 = cv2.VideoCapture(gst0, cv2.CAP_GSTREAMER)
    cap1 = cv2.VideoCapture(gst1, cv2.CAP_GSTREAMER)

    if not (cap0.isOpened() and cap1.isOpened()):
        print("❌ Could not open both cameras simultaneously.")
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

    connected_cams = detect_cameras()
    if not connected_cams:
        print("\n❌ No Raspberry Pi cameras detected.")
    else:
        print(f"\n✅ Detected {len(connected_cams)} camera(s): {connected_cams}")

        # Test each camera sequentially
        for cam_id in connected_cams:
            print(f"\n🔎 Opening camera {cam_id} individually...")
            test_camera(cam_id)
            print(f"✅ Camera {cam_id} test complete.\n")
            time.sleep(1)

        print("\nℹ️ Dual camera preview skipped (not supported on Jetson Nano).")

    print("\n✅ Camera check complete.")

