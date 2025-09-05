import cv2
import numpy as np
import subprocess
import time
import os

def check_cameras():
    # Check for video devices
    try:
        result = subprocess.run(['ls', '-l', '/dev/video*'], 
                              capture_output=True, text=True)
        print("Available video devices:")
        print(result.stdout)
    except:
        print("No video devices found in /dev/video*")
    
    # Check for nvargus-daemon
    try:
        result = subprocess.run(['systemctl', 'status', 'nvargus-daemon'],
                              capture_output=True, text=True)
        print("\nnvargus-daemon status:")
        print(result.stdout)
    except:
        print("Could not check nvargus-daemon status")
        
    # Check for camera modules
    try:
        result = subprocess.run(['ls', '-l', '/sys/class/video4linux'],
                              capture_output=True, text=True)
        print("\nVideo4Linux devices:")
        print(result.stdout)
    except:
        print("No Video4Linux devices found")

def gstreamer_pipeline(sensor_id=0, capture_width=1920, capture_height=1080, 
                      display_width=960, display_height=540, framerate=30, flip_method=0):
    return (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        f"video/x-raw(memory:NVMM), width=(int){capture_width}, height=(int){capture_height}, "
        f"format=(string)NV12, framerate=(fraction){framerate}/1 ! "
        f"nvvidconv flip-method={flip_method} ! "
        f"video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"
    )

def try_gstreamer_camera(sensor_id=0):
    print(f"\nTrying GStreamer pipeline with sensor_id={sensor_id}")
    pipeline = gstreamer_pipeline(
        sensor_id=sensor_id,
        capture_width=1280,    # Reduced resolution
        capture_height=720,
        display_width=640,
        display_height=360,
        framerate=30,
        flip_method=0
    )
    print("Pipeline:", pipeline)
    
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    return test_camera(cap, f"GStreamer Camera {sensor_id}")

def try_direct_camera(device_id=0):
    print(f"\nTrying direct camera access with device_id={device_id}")
    cap = cv2.VideoCapture(device_id)
    return test_camera(cap, f"Direct Camera {device_id}")

def test_camera(cap, name):
    if not cap.isOpened():
        print(f"Failed to open {name}")
        return False
        
    print(f"Successfully opened {name}")
    success = False
    
    try:
        # Try to read 5 frames
        for i in range(5):
            ret, frame = cap.read()
            if ret:
                print(f"Successfully read frame {i+1}")
                cv2.imshow(name, frame)
                if cv2.waitKey(1000) & 0xFF == ord('q'):  # Wait for 1 second, break if 'q' pressed
                    break
                success = True
            else:
                print(f"Failed to read frame {i+1}")
    finally:
        cap.release()
        cv2.destroyWindow(name)
        time.sleep(1)
    
    return success

def main():
    print("Checking camera devices...")
    check_cameras()
    
    # Try both GStreamer and direct access for each potential camera
    success = False
    
    # Try GStreamer first (usually works better for CSI cameras on Jetson)
    for sensor_id in range(2):
        if try_gstreamer_camera(sensor_id):
            success = True
            print(f"\nSuccessfully accessed camera using GStreamer with sensor_id={sensor_id}")
    
    # If GStreamer failed, try direct access
    if not success:
        print("\nGStreamer access failed, trying direct camera access...")
        for device_id in range(2):
            if try_direct_camera(device_id):
                success = True
                print(f"\nSuccessfully accessed camera using direct access with device_id={device_id}")
    
    if not success:
        print("\nFailed to access any cameras. Please check:")
        print("1. Camera connections (CSI cables properly seated)")
        print("2. Run 'sudo systemctl restart nvargus-daemon'")
        print("3. Check 'dmesg | grep -i camera' for kernel messages")
        print("4. Verify camera compatibility with Jetson Orin Nano")

    # Main loop is now handled in the main() function above
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()