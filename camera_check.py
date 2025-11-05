#!/usr/bin/env python3
"""
camera_check.py
----------------
Robust Jetson Nano camera tester.
- Detects connected CSI cameras
- Confirms actual frame capture before declaring a camera 'working'
- Handles missing/unplugged cameras gracefully
"""

import cv2
import time
import os

def camera_available(sensor_id):
    """Try to open and grab one frame to confirm a real working camera."""
    gst = (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        "video/x-raw(memory:NVMM),width=640,height=480,framerate=30/1 ! "
        "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink"
    )
    cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        cap.release()
        return False

    # Try to read one frame
    ret, _ = cap.read()
    cap.release()
    return ret  # True if a valid frame was read


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
            print(f"⚠️ Frame capture failed for camera {sensor_id}.")
            break  # exit instead of looping forever

        cv2.imshow(f"Camera {sensor_id}", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Camera {sensor_id} test complete.")


if __name__ == "__main__":
    print("🚀 Jetson Nano Camera Check (Robust Mode)")
    print("------------------------------------------")

    os.system("ls /dev/video* || echo 'No /dev/video devices found.'")

    detected_cams = []
    for cam_id in range(2):  # Check sensor-id 0 and 1
        if camera_available(cam_id):
            detected_cams.append(cam_id)

    if not detected_cams:
        print("\n❌ No working cameras detected.")
    else:
        print(f"\n✅ Working camera(s) detected: {detected_cams}")
        for cam_id in detected_cams:
            test_camera(cam_id)
            time.sleep(1)

    print("\n✅ Camera check complete.")
