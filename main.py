"""
main.py

Main application entry point (Desktop Version).
"""

import cv2
import mediapipe as mp
import sys
import os

# Import from source package
from src.config import *
from src.utils.geometry import calculate_ear
from src.utils.sound import trigger_alarm, deactivate_alarm

def initialize_landmarker():
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    # Use dynamic path from config
    model_path = os.path.join(MODELS_DIR, "face_landmarker.task")

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
    print("[INFO] Starting Drowsiness Detection System (Desktop)...")
    
    cap = cv2.VideoCapture(WEBCAM_ID)
    if not cap.isOpened():
        print(f"[ERROR] Could not open webcam {WEBCAM_ID}")
        return

    landmarker = initialize_landmarker()
    
    COUNTER = 0
    ALARM_ON = False
    
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    frame_timestamp_ms = 0

    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
               continue

            height, width, _ = image.shape
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

            frame_timestamp_ms += 33
            results = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

            if results.face_landmarks:
                face_landmarks = results.face_landmarks[0]
                
                left_eye_points = []
                right_eye_points = []

                for idx in LEFT_EYE:
                    lm = face_landmarks[idx]
                    left_eye_points.append((int(lm.x * width), int(lm.y * height)))
                
                for idx in RIGHT_EYE:
                    lm = face_landmarks[idx]
                    right_eye_points.append((int(lm.x * width), int(lm.y * height)))

                left_ear = calculate_ear(left_eye_points)
                right_ear = calculate_ear(right_eye_points)
                avg_ear = (left_ear + right_ear) / 2.0
                
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
