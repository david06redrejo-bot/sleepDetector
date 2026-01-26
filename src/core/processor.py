"""
src/core/processor.py

Handles frame-by-frame processing for the Streamlit WebRTC component.
"""

import av
import cv2
import mediapipe as mp
import time
import os
import threading
from typing import List, Tuple

# Updated Imports
from src.config import *
from src.utils.geometry import calculate_ear

class DrowsinessProcessor:
    def __init__(self):
        self.frame_count = 0
        self.alarm_on = False
        self.ear_history = []
        self.current_ear = 0.0
        
        self.lock = threading.Lock()

        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        # Dynamic Model Path from config.MODELS_DIR
        model_path = os.path.join(MODELS_DIR, "face_landmarker.task")
        
        try:
            with open(model_path, 'r'): pass
        except FileNotFoundError:
            # Fallback or error logging
            print(f"Model not found at {model_path}")
        
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
        
        self.landmarker = FaceLandmarker.create_from_options(options)
        self.timestamp_ms = 0
        self.threshold = EYE_ASPECT_RATIO_THRESHOLD

    def update_threshold(self, new_threshold):
        with self.lock:
            self.threshold = new_threshold

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        height, width, _ = image.shape

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

        self.timestamp_ms += 33
        results = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)
        
        current_ear = 0.0
        status_color = (0, 255, 0)

        if results.face_landmarks:
            face_landmarks = results.face_landmarks[0]
            
            left_eye_idxs = [33, 160, 158, 133, 153, 144]
            right_eye_idxs = [362, 385, 387, 263, 373, 380]

            left_points = [(int(face_landmarks[i].x * width), int(face_landmarks[i].y * height)) for i in left_eye_idxs]
            right_points = [(int(face_landmarks[i].x * width), int(face_landmarks[i].y * height)) for i in right_eye_idxs]

            left_ear = calculate_ear(left_points)
            right_ear = calculate_ear(right_points)
            current_ear = (left_ear + right_ear) / 2.0

            with self.lock:
                self.current_ear = current_ear
                
                if current_ear < self.threshold:
                    self.frame_count += 1
                    if self.frame_count >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        self.alarm_on = True
                        status_color = (0, 0, 255)
                else:
                    self.frame_count = 0
                    self.alarm_on = False

            for (x, y) in left_points + right_points:
                cv2.circle(image, (x, y), 1, (0, 255, 255), -1)

            if self.alarm_on:
                cv2.putText(image, "WAKE UP!", (50, height // 2), 
                           cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 0, 255), 4)

        cv2.putText(image, f"EAR: {current_ear:.2f}", (width - 160, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

        return av.VideoFrame.from_ndarray(image, format="bgr24")
