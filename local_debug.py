"""
local_debug.py

A standalone script to test Drowsiness Detection locally using OpenCV windows.
This bypasses Streamlit and WebRTC to verify:
1. Webcam access
2. MediaPipe model loading
3. Logic correctness (EAR calculation)
"""

import cv2
import mediapipe as mp
import time
import sys
import os
import numpy as np

# Adjust path to ensure src imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import *
from src.utils.geometry import calculate_ear
from src.utils.sound import trigger_alarm, deactivate_alarm

def initialize_landmarker():
    """
    Sets up the MediaPipe Face Landmarker (Tasks API).
    """
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    # Model path
    model_path = os.path.join(MODELS_DIR, "face_landmarker.task")

    if not os.path.exists(model_path):
        print(f"[ERROR] Model not found at {model_path}")
        sys.exit(1)

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    
    return FaceLandmarker.create_from_options(options)

def main():
    print("[INFO] Starting Local Debug Mode (OpenCV)...")
    print(f"[INFO] Model Path: {os.path.join(MODELS_DIR, 'face_landmarker.task')}")
    
    cap = cv2.VideoCapture(WEBCAM_ID)
    if not cap.isOpened():
        print(f"[ERROR] Could not open webcam with ID {WEBCAM_ID}")
        return

    landmarker = initialize_landmarker()
    
    # State Variables
    COUNTER = 0
    ALARM_ON = False
    
    # Landmark Indices (Left and Right Eyes)
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    # Timestamp for MediaPipe video mode
    frame_timestamp_ms = 0

    print("[INFO] Press 'ESC' to exit.")

    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
               print("[WARNING] Empty frame ignored.")
               continue

            height, width, _ = image.shape
            
            # Convert BGR (OpenCV) to RGB (MediaPipe)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

            # Inference
            frame_timestamp_ms += 33
            results = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

            # Default text
            text_color = (0, 255, 0)
            status_text = "Status: AWAKE"

            if results.face_landmarks:
                face_landmarks = results.face_landmarks[0]
                
                left_eye_points = []
                right_eye_points = []

                # Extract Normalized Coordinates -> Pixel Coordinates
                for idx in LEFT_EYE:
                    lm = face_landmarks[idx]
                    left_eye_points.append((int(lm.x * width), int(lm.y * height)))
                
                for idx in RIGHT_EYE:
                    lm = face_landmarks[idx]
                    right_eye_points.append((int(lm.x * width), int(lm.y * height)))

                # Geometry Logic
                left_ear = calculate_ear(left_eye_points)
                right_ear = calculate_ear(right_eye_points)
                avg_ear = (left_ear + right_ear) / 2.0
                
                # Check Logic
                if avg_ear < EYE_ASPECT_RATIO_THRESHOLD:
                    COUNTER += 1
                    if COUNTER >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        status_text = "Status: DROWSY!"
                        text_color = (0, 0, 255)
                        if not ALARM_ON:
                            ALARM_ON = True
                            trigger_alarm()
                        
                        cv2.putText(image, "DROWSINESS ALERT!", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.rectangle(image, (0,0), (width, height), (0,0,255), 5)
                else:
                    COUNTER = 0
                    if ALARM_ON:
                        ALARM_ON = False
                        deactivate_alarm()
                
                # Visual Feedback
                cv2.putText(image, f"EAR: {avg_ear:.2f}", (width - 150, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                for (x, y) in left_eye_points + right_eye_points:
                    cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
            
            # Draw status
            cv2.putText(image, status_text, (10, height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

            cv2.imshow('Local Debug Mode (Press ESC to quit)', image)
            
            if cv2.waitKey(5) & 0xFF == 27:
                break
                
    finally:
        landmarker.close()
        cap.release()
        cv2.destroyAllWindows()
        deactivate_alarm()
        print("[INFO] System Terminated.")

if __name__ == "__main__":
    main()
