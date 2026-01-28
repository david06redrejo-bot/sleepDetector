"""
main.py

Drowsiness Detection System - Streamlit Web App (Hugging Face Compatible)
Premium Safety Monitoring Dashboard with Real-Time Detection
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
from src.utils.sound import trigger_alarm, deactivate_alarm
from src.rtc_config import get_rtc_configuration

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="NeuroVigilance | Drowsiness Detection",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# LOAD CUSTOM CSS
# =============================================================================
def load_css(file_name):
    """Load and inject custom CSS styles."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    load_css(os.path.join(ASSETS_DIR, 'style.css'))
except Exception as e:
    print(f"Warning: Could not load CSS: {e}")

# =============================================================================
# AUDIO HANDLING (Client-Side)
# =============================================================================
def get_audio_html(file_path):
    """Generate HTML audio element with base64 encoded alarm.wav"""
    try:
        with open(file_path, "rb") as f:
            b64_audio = base64.b64encode(f.read()).decode()
        return f'''
            <audio autoplay loop>
                <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
            </audio>
        '''
    except FileNotFoundError:
        return ""

AUDIO_HTML = get_audio_html(ALARM_SOUND_PATH)

# =============================================================================
# VIDEO PROCESSOR CLASS
# =============================================================================
class DrowsinessProcessor(VideoProcessorBase):
    """MediaPipe-based drowsiness detection processor for WebRTC streams."""
    
    def __init__(self):
        self.frame_lock = threading.Lock()
        self.alarm_on = False
        self.current_ear = 0.0
        
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
        
        # Eye landmark indices
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        self.consec_frames = 0
        
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """Process incoming video frame for drowsiness detection."""
        image = frame.to_ndarray(format="bgr24")
        height, width, _ = image.shape
        
        # MediaPipe expects RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        # Update timestamp (simulating ~30fps for MP tracking)
        self.timestamp_ms += 33
        
        try:
            results = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)
            is_drowsy_now = False
            avg_ear = 0.0
            
            if results.face_landmarks:
                face_landmarks = results.face_landmarks[0]
                
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
                
                # Draw EAR value with styled background
                ear_text = f"EAR: {avg_ear:.3f}"
                (text_width, text_height), baseline = cv2.getTextSize(
                    ear_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                
                # Semi-transparent background for EAR display
                overlay = image.copy()
                cv2.rectangle(overlay, 
                             (width - text_width - 30, 10), 
                             (width - 10, text_height + 25), 
                             (15, 23, 42), -1)
                cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
                
                # EAR text
                cv2.putText(image, ear_text, (width - text_width - 20, text_height + 17),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (34, 211, 238), 2)
                
                # Draw eye landmark points
                for (x, y) in left_eye_points + right_eye_points:
                    cv2.circle(image, (x, y), 2, (16, 185, 129), -1)
                    cv2.circle(image, (x, y), 4, (16, 185, 129), 1)
                
                # Drowsiness detection logic
                if avg_ear < EYE_ASPECT_RATIO_THRESHOLD:
                    self.consec_frames += 1
                    if self.consec_frames >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        is_drowsy_now = True
                        
                        # Draw alert overlay
                        overlay = image.copy()
                        cv2.rectangle(overlay, (0, 0), (width, 60), (239, 68, 68), -1)
                        cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)
                        
                        # Alert text with icon
                        alert_text = "⚠ DROWSINESS DETECTED"
                        cv2.putText(image, alert_text, (20, 40),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
                        
                        # Alert border
                        cv2.rectangle(image, (0, 0), (width-1, height-1), (239, 68, 68), 4)
                else:
                    self.consec_frames = 0
            
            # Thread-safe update of alarm state and EAR
            with self.frame_lock:
                self.alarm_on = is_drowsy_now
                self.current_ear = avg_ear
                
        except Exception as e:
            print(f"Error in processing: {e}")
            
        return av.VideoFrame.from_ndarray(image, format="bgr24")

# =============================================================================
# SIDEBAR CONFIGURATION
# =============================================================================
def render_sidebar():
    """Render the premium sidebar with system info."""
    with st.sidebar:
        # Logo/Brand section
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🧠</div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; 
                        font-size: 1.1rem; letter-spacing: 0.05em; color: #f8fafc;">
                NEURO<span style="color: #22d3ee;">VIGILANCE</span>
            </div>
            <div style="font-size: 0.7rem; color: #64748b; letter-spacing: 0.1em; 
                        text-transform: uppercase; margin-top: 4px;">
                Safety Monitoring System
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # System Status
        st.markdown("### 📊 System Status")
        
        status_col1, status_col2 = st.columns(2)
        with status_col1:
            st.markdown("""
            <div class="metric-container" style="padding: 12px; text-align: center;">
                <div style="font-size: 0.65rem; color: #64748b; text-transform: uppercase; 
                            letter-spacing: 0.1em; margin-bottom: 4px;">Model</div>
                <div style="font-size: 0.85rem; color: #10b981; font-weight: 600;">● Active</div>
            </div>
            """, unsafe_allow_html=True)
        with status_col2:
            st.markdown("""
            <div class="metric-container" style="padding: 12px; text-align: center;">
                <div style="font-size: 0.65rem; color: #64748b; text-transform: uppercase; 
                            letter-spacing: 0.1em; margin-bottom: 4px;">Camera</div>
                <div style="font-size: 0.85rem; color: #22d3ee; font-weight: 600;">Ready</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detection Parameters (Display Only)
        st.markdown("### ⚙️ Detection Parameters")
        
        st.markdown(f"""
        <div class="metric-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 0.75rem; color: #94a3b8;">EAR Threshold</span>
                <span style="font-family: 'JetBrains Mono', monospace; color: #22d3ee; font-weight: 600;">
                    {EYE_ASPECT_RATIO_THRESHOLD}
                </span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.75rem; color: #94a3b8;">Consec. Frames</span>
                <span style="font-family: 'JetBrains Mono', monospace; color: #22d3ee; font-weight: 600;">
                    {EYE_ASPECT_RATIO_CONSEC_FRAMES}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ About This System"):
            st.markdown("""
            **NeuroVigilance** uses advanced computer vision and 
            MediaPipe's Face Mesh to monitor eye aspect ratio (EAR) 
            in real-time.
            
            When drowsiness is detected (eyes closed for consecutive 
            frames), an audible alarm is triggered to alert the user.
            
            ---
            
            **Tech Stack:**
            - 🔬 MediaPipe Face Landmarker
            - 🎥 WebRTC Streaming
            - 🐍 Streamlit Framework
            """)

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """Main application entry point."""
    
    # Render sidebar
    render_sidebar()
    
    # ==========================================================================
    # HERO SECTION
    # ==========================================================================
    st.markdown("""
    <div class="hero-badge">
        <span>Real-Time Monitoring</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.title("Drowsiness Detection System")
    
    st.markdown("""
    <p class="hero-subtitle">
        AI-powered safety monitoring using computer vision to detect driver fatigue in real-time
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================================================
    # MAIN CONTENT LAYOUT
    # ==========================================================================
    
    # Video Feed Section
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <span style="font-family: 'Space Grotesk', sans-serif; font-size: 0.8rem; 
                     font-weight: 600; color: #64748b; text-transform: uppercase; 
                     letter-spacing: 0.1em;">
            📹 Live Camera Feed
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for centered video with metrics on side
    col_left, col_center, col_right = st.columns([1, 3, 1])
    
    with col_center:
        # Video container with premium styling
        st.markdown('<div class="video-container">', unsafe_allow_html=True)
        
        # WebRTC Streamer with STUN + TURN configuration for reliable connectivity
        # Uses Metered.ca Open Relay TURN servers (20GB free/month)
        ctx = webrtc_streamer(
            key="drowsiness-detection", 
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=get_rtc_configuration(),
            video_processor_factory=DrowsinessProcessor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================================================
    # STATUS & METRICS ROW
    # ==========================================================================
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">System Status</div>
            <div class="status-safe" style="margin-top: 8px; padding: 10px 16px; border-radius: 8px;">
                ● Monitoring Active
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Eye Aspect Ratio</div>
            <div style="display: flex; align-items: baseline; gap: 4px; margin-top: 4px;">
                <span class="metric-value">--</span>
                <span class="metric-unit">EAR</span>
            </div>
            <div class="ear-gauge">
                <div class="ear-gauge-fill" style="width: 70%;"></div>
                <div class="ear-gauge-threshold" style="left: 30%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Detection Sensitivity</div>
            <div style="display: flex; align-items: baseline; gap: 4px; margin-top: 4px;">
                <span class="metric-value">High</span>
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 8px;">
                Optimized for safety
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================================================
    # INFO SECTION
    # ==========================================================================
    st.info("""
    **📌 Quick Start:** Click "START" above to enable your camera. Grant camera permissions when prompted.
    The system will monitor your eye movements and trigger an audio alarm if drowsiness is detected.
    """)
    
    # ==========================================================================
    # AUDIO PLACEHOLDER
    # ==========================================================================
    sound_placeholder = st.empty()
    
    # ==========================================================================
    # POLLING LOOP FOR AUDIO TRIGGER
    # ==========================================================================
    if ctx.state.playing:
        while True:
            if ctx.video_processor:
                drowsy = False
                with ctx.video_processor.frame_lock:
                    drowsy = ctx.video_processor.alarm_on
                
                if drowsy:
                    # Inject audio HTML - plays alarm.wav
                    sound_placeholder.markdown(AUDIO_HTML, unsafe_allow_html=True)
                else:
                    # Remove audio element to stop playback
                    sound_placeholder.empty()
            
            # Fast polling (50ms)
            time.sleep(0.05)
    
    # ==========================================================================
    # FOOTER
    # ==========================================================================
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="app-footer">
        <div class="footer-content">
            <div class="footer-brand">
                🧠 NeuroVigilance — Drowsiness Detection System
            </div>
            <div class="footer-tech">
                <span>MediaPipe</span>
                <span>OpenCV</span>
                <span>Streamlit</span>
                <span>WebRTC</span>
            </div>
            <div style="font-size: 0.75rem; color: #475569; margin-top: 8px;">
                Built for safety • Real-time AI monitoring
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    main()
