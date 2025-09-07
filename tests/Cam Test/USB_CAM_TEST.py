import cv2
import numpy as np

def test_usb_camera():
    # Try to get the first video device (usually USB camera)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    # Print camera properties
    print(f"Frame Width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    print(f"Frame Height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    
    try:
        while True:
            # Read a frame from the camera
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Could not read frame.")
                break
            
            # Display the frame
            cv2.imshow('USB Camera Test', frame)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Starting USB camera test...")
    print("Press 'q' to quit")
    test_usb_camera()
