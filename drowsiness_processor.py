"""
drowsiness_processor.py

Handles frame-by-frame processing for the Streamlit WebRTC component.
"""

import av
import cv2
import mediapipe as mp
import time
import os
import threading
from typing import List, Tuple

from config import *  # Import constants (defaults)
from utils.geometry import calculate_ear

class DrowsinessProcessor:
    def __init__(self):
        self.frame_count = 0
        self.alarm_on = False
        self.ear_history = []
        self.current_ear = 0.0
        
        # Lock for thread-safe variable access
        self.lock = threading.Lock()

        # Initialize MediaPipe (same as before, but in class)
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        model_path = os.path.join("models", "face_landmarker.task")
        
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
        
        # User-adjustable threshold (can be updated from UI)
        self.threshold = EYE_ASPECT_RATIO_THRESHOLD

    def update_threshold(self, new_threshold):
        with self.lock:
            self.threshold = new_threshold

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        Receive a frame from the client, process it, and return the annotated frame.
        """
        image = frame.to_ndarray(format="bgr24")
        height, width, _ = image.shape

        # Convert to RGB for MediaPipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

        self.timestamp_ms += 33 # Assume ~30fps
        
        # Inference
        results = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)
        
        current_ear = 0.0
        status_color = (0, 255, 0) # Green

        if results.face_landmarks:
            face_landmarks = results.face_landmarks[0]
            
            # Extract Eyes
            left_eye_idxs = [33, 160, 158, 133, 153, 144]
            right_eye_idxs = [362, 385, 387, 263, 373, 380]

            left_points = [(int(face_landmarks[i].x * width), int(face_landmarks[i].y * height)) for i in left_eye_idxs]
            right_points = [(int(face_landmarks[i].x * width), int(face_landmarks[i].y * height)) for i in right_eye_idxs]

            # Logic
            left_ear = calculate_ear(left_points)
            right_ear = calculate_ear(right_points)
            current_ear = (left_ear + right_ear) / 2.0

            # Thread-safe state update
            with self.lock:
                self.current_ear = current_ear
                
                if current_ear < self.threshold:
                    self.frame_count += 1
                    if self.frame_count >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        self.alarm_on = True
                        status_color = (0, 0, 255) # Red
                else:
                    self.frame_count = 0
                    self.alarm_on = False

            # Visualization
            for (x, y) in left_points + right_points:
                cv2.circle(image, (x, y), 1, (0, 255, 255), -1)

            if self.alarm_on:
                cv2.putText(image, "WAKE UP!", (50, height // 2), 
                           cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 0, 255), 4)

        # Visualize EAR on frame
        cv2.putText(image, f"EAR: {current_ear:.2f}", (width - 160, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

        return av.VideoFrame.from_ndarray(image, format="bgr24")
