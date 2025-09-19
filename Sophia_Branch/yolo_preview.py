# live_preview3.py
import time
import threading
import cv2
import numpy as np
from picamera2 import Picamera2
from ultralytics import YOLO

MODEL_PATH = "/home/Cat/yolo/yolov8n_ncnn_model"
INFERENCE_SIZE = (320, 240)
RUN_INFERENCE_EVERY = 0.5

# Shared state
latest_detections = []
frame_lock = threading.Lock()
shared_rgb_frame = None
picam2 = None
model = None

def start_camera():
    """Initialize camera and YOLO model, start inference thread."""
    global picam2, model
    model = YOLO(MODEL_PATH, task="detect")

    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
    picam2.start()
    time.sleep(1)

    threading.Thread(target=_yolo_thread, daemon=True).start()

def _yolo_thread():
    global latest_detections
    while True:
        time.sleep(RUN_INFERENCE_EVERY)
        with frame_lock:
            if shared_rgb_frame is None:
                continue
            small_frame = cv2.resize(shared_rgb_frame, INFERENCE_SIZE)

        results = model(small_frame, verbose=False)
        boxes = []
        for box in results[0].boxes:
            conf = float(box.conf[0])
            x_min, y_min, x_max, y_max = box.xyxy[0]

            # Scale to full frame
            scale_x = 640 / INFERENCE_SIZE[0]
            scale_y = 480 / INFERENCE_SIZE[1]
            x_min = int(x_min * scale_x)
            y_min = int(y_min * scale_y)
            x_max = int(x_max * scale_x)
            y_max = int(y_max * scale_y)
            boxes.append((x_min, y_min, x_max, y_max, conf))

        with frame_lock:
            latest_detections = boxes

def get_latest_frame():
    """Return latest frame from camera (RGB)."""
    global shared_rgb_frame
    frame_rgb = picam2.capture_array()
    with frame_lock:
        shared_rgb_frame = frame_rgb.copy()
        return frame_rgb

def get_latest_detections():
    """Return latest YOLO detections."""
    with frame_lock:
        return latest_detections.copy()

def show_preview(frame, detections):
    """Display frame with bounding boxes in a window."""
    display = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    for (x1, y1, x2, y2, conf) in detections:
        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(display, f"{conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.imshow("YOLO Detection", display)
    return cv2.waitKey(1) & 0xFF