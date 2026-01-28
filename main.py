"""
main.py

Drowsiness Detection System - Streamlit Web App (Hugging Face Compatible)
Migrated from desktop OpenCV to Streamlit-WebRTC.
"""

import av
import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import base64
import threading
import time
import os
import sys

# Import from source package
from src.config import *
from src.utils.geometry import calculate_ear

# Load Custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    load_css(os.path.join(ASSETS_DIR, 'style.css'))
except Exception as e:
    print(f"Warning: Could not load CSS: {e}")

# Audio Handling (Client-Side)
def get_audio_html(file_path):
    """
    Generates an HTML audio player that autoplays independent of the browser's
    strict autoplay policies (works best when triggered by UI updates).
    """
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            b64_audio = base64.b64encode(data).decode()
            
        md = f"""
            <audio autoplay loop>
            <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
            Your browser does not support the audio element.
            </audio>
            """
        return md
    except FileNotFoundError:
        return ""

AUDIO_HTML = get_audio_html(ALARM_SOUND_PATH)

# MediaPipe Initialization (Lazy Loading)
class DrowsinessProcessor(VideoProcessorBase):
    def __init__(self):
        self.frame_lock = threading.Lock()
        self.alarm_on = False
        
        # Initialize MediaPipe
        self.BaseOptions = mp.tasks.BaseOptions
        self.FaceLandmarker = mp.tasks.vision.FaceLandmarker
        self.FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        self.VisionRunningMode = mp.tasks.vision.RunningMode
        
        # Path to model
        model_path = os.path.join(MODELS_DIR, "face_landmarker.task")
        
        options = self.FaceLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path=model_path),
            running_mode=self.VisionRunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.landmarker = self.FaceLandmarker.create_from_options(options)
        self.timestamp_ms = 0
        
        # Constants
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        self.consec_frames = 0
        
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        Receives a frame from the WebRTC stream, processes it, and returns it.
        """
        image = frame.to_ndarray(format="bgr24")
        
        # MediaPipe expects RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        # Update timestamp (simulating 30fps roughly for MP tracking)
        self.timestamp_ms += 33
        
        try:
            results = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)
            
            is_drowsy_now = False
            
            if results.face_landmarks:
                face_landmarks = results.face_landmarks[0]
                height, width, _ = image.shape
                
                left_eye_points = []
                right_eye_points = []

                for idx in self.LEFT_EYE:
                    lm = face_landmarks[idx]
                    left_eye_points.append((int(lm.x * width), int(lm.y * height)))
                
                for idx in self.RIGHT_EYE:
                    lm = face_landmarks[idx]
                    right_eye_points.append((int(lm.x * width), int(lm.y * height)))

                left_ear = calculate_ear(left_eye_points)
                right_ear = calculate_ear(right_eye_points)
                avg_ear = (left_ear + right_ear) / 2.0
                
                # Draw EAR
                cv2.putText(image, f"EAR: {avg_ear:.2f}", (width - 150, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Draw Eyes
                for (x, y) in left_eye_points + right_eye_points:
                    cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
                
                # Check Logic
                if avg_ear < EYE_ASPECT_RATIO_THRESHOLD:
                    self.consec_frames += 1
                    if self.consec_frames >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        is_drowsy_now = True
                        # Parse Visual Alert on Frame
                        cv2.putText(image, "DROWSINESS ALERT!", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.rectangle(image, (0,0), (width, height), (0,0,255), 5)
                else:
                    self.consec_frames = 0
            
            # Thread-safe update of alarm state
            with self.frame_lock:
                self.alarm_on = is_drowsy_now
                
        except Exception as e:
            print(f"Error in processing: {e}")
            
        return av.VideoFrame.from_ndarray(image, format="bgr24")

def main():
    st.title("😴 Real-Time Drowsiness Detector")
    st.markdown("### Powered by MediaPipe & Streamlit")
    
    st.info("Ensure you grant camera permission. The alarm will sound if you close your eyes for a few seconds.")

    # WebRTC Streamer
    ctx = webrtc_streamer(
        key="drowsiness-detection", 
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        },
        video_processor_factory=DrowsinessProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    # Placeholder for Client-Side Audio
    sound_placeholder = st.empty()
    
    # Polling Loop for Audio Trigger
    if ctx.state.playing:
        while True:
            if ctx.video_processor:
                drowsy = False
                with ctx.video_processor.frame_lock:
                    drowsy = ctx.video_processor.alarm_on
                
                if drowsy:
                    # Inject Audio HTML (Autoplay Loop)
                    sound_placeholder.markdown(AUDIO_HTML, unsafe_allow_html=True)
                else:
                    # Remove Audio HTML to stop sound
                    sound_placeholder.empty()
            
            # Prevent high CPU usage in polling loop
            time.sleep(0.1)

if __name__ == "__main__":
    main()
