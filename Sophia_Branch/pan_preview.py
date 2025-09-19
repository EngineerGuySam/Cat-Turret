# controller.py
import time
import cv2
import threading
import pan_tilt   # <-- your full pan_tilt.py, untouched
from live_preview3 import start_camera, get_latest_frame, get_latest_detections, show_preview

CONFIDENCE_THRESHOLD = 0.7

# Flag to control scanning thread
scanning = True

def scan_loop():
    """Background thread for idle scanning when no detections are present."""
    while True:
        if scanning:
            pan_tilt.idle_scan()
        else:
            time.sleep(0.05)  # yield CPU when scanning is paused

def main():
    global scanning
    print("System starting...")
    start_camera()

    # Start scanning thread
    threading.Thread(target=scan_loop, daemon=True).start()

    try:
        while True:
            frame = get_latest_frame()
            detections = get_latest_detections()

            # Show live preview
            key = show_preview(frame, detections)
            if key in [ord("q"), 27]:
                break

            if not detections:
                scanning = True   # enable idle scanning
                continue

            # We have a detection, stop scanning and track
            scanning = False

            # Pick the most confident detection
            x1, y1, x2, y2, conf = max(detections, key=lambda d: d[4])
            if conf < CONFIDENCE_THRESHOLD:
                continue

            # Detection center
            target_x = (x1 + x2) // 2
            target_y = (y1 + y2) // 2

            # Map to servo ranges
            pan = int(500 + (target_x / 640) * (2500 - 500))
            tilt = int(500 + (target_y / 480) * (1600 - 500))

            # Smoothly move servos using your pan_tilt function
            pan_tilt.smooth_move_timed(pan, tilt)

            print(f"Tracking at ({target_x},{target_y}), conf={conf:.2f}")

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        pan_tilt.cleanup()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()