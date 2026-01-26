"""
main.py

Main application entry point.
Orchestrates Video Capture, MediaPipe Inference, and State Estimation.
"""

import cv2
import mediapipe as mp
import time
import sys
import os

from config import *
from utils.geometry import calculate_ear
from utils.alarm import trigger_alarm, deactivate_alarm

def initialize_landmarker():
    """
    Sets up the MediaPipe Face Landmarker (Tasks API).
    """
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    # Model path is now in the models/ subdirectory
    model_path = os.path.join("models", "face_landmarker.task")

    try:
        with open(model_path, 'r'): pass
    except FileNotFoundError:
        print(f"[ERROR] Model bundle missing at {model_path}.")
        sys.exit(1)

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False
    )
    
    return FaceLandmarker.create_from_options(options)

def main():
    print("[INFO] Starting Drowsiness Detection System...")
    
    cap = cv2.VideoCapture(WEBCAM_ID)
    if not cap.isOpened():
        print(f"[ERROR] Could not open webcam {WEBCAM_ID}")
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

    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
               continue

            height, width, _ = image.shape
            
            # Convert BGR (OpenCV) to RGB (MediaPipe)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

            # Inference
            frame_timestamp_ms += 33
            results = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

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
                
                # Calibration print
                # print(f"[DEBUG] EAR: {avg_ear:.3f}")

                # State Machine
                if avg_ear < EYE_ASPECT_RATIO_THRESHOLD:
                    COUNTER += 1
                    if COUNTER >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        if not ALARM_ON:
                            ALARM_ON = True
                            trigger_alarm()
                        
                        cv2.putText(image, "DROWSINESS ALERT!", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
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

            cv2.imshow('SleepDetector v1.0', image)
            
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
