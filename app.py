"""
app.py

The Cyberpunk Drowsiness Detection Web Application.
"""

import streamlit as st
import time
import base64
import os
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import altair as alt
import pandas as pd
from datetime import datetime

# Updated Imports
from src.core.processor import DrowsinessProcessor
import src.config as config

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NEURO-VIGILANCE // SLEEP DETECTOR",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS using config.ASSETS_DIR
css_path = os.path.join(config.ASSETS_DIR, "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# AUDIO HANDLING (Client-Side Injection)
# -----------------------------------------------------------------------------
def get_audio_html(file_path):
    """Encodes the audio file to base64 for HTML embedding."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio autoplay loop><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>'
    except FileNotFoundError:
        return ""

ALARM_AUDIO_HTML = get_audio_html(config.ALARM_SOUND_PATH)
alarm_placeholder = st.empty()

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.title("SYSTEM CONTROL")
st.sidebar.markdown("---")

threshold_slider = st.sidebar.slider(
    "SENSITIVITY (EAR THRESHOLD)", 
    min_value=0.15, 
    max_value=0.35, 
    value=config.EYE_ASPECT_RATIO_THRESHOLD,
    step=0.01
)

st.sidebar.markdown("### SYSTEM STATUS")
status_indicator = st.sidebar.empty()

# -----------------------------------------------------------------------------
# MAIN LAYOUT
# -----------------------------------------------------------------------------
st.title("NEURO-VIGILANCE v2.0")
st.markdown("##### REAL-TIME DROWSINESS MONITORING SYSTEM")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### OPTICAL SENSOR FEED")
    
    ctx = webrtc_streamer(
        key="drowsiness-detection",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        video_processor_factory=DrowsinessProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with col2:
    st.markdown("### BIOMETRIC TELEMETRY")
    chart_placeholder = st.empty()
    metric_placeholder = st.empty()

# -----------------------------------------------------------------------------
# MAIN EVENT LOOP
# -----------------------------------------------------------------------------
if ctx.video_processor:
    ctx.video_processor.update_threshold(threshold_slider)
    
    ear_data = []

    while ctx.state.playing:
        with ctx.video_processor.lock:
            current_ear = ctx.video_processor.current_ear
            is_alarm = ctx.video_processor.alarm_on
        
        timestamp = datetime.now()
        ear_data.append({"Time": timestamp, "EAR": current_ear})
        
        if len(ear_data) > 50:
            ear_data.pop(0)
            
        df = pd.DataFrame(ear_data)
        chart = alt.Chart(df).mark_line(color='#66fcf1').encode(
            x=alt.X('Time', axis=alt.Axis(format='%H:%M:%S', title='Time')),
            y=alt.Y('EAR', scale=alt.Scale(domain=[0, 0.4])),
        ).properties(height=300)
        
        chart_placeholder.altair_chart(chart, use_container_width=True)

        if is_alarm:
            metric_placeholder.markdown(
                '<div class="metric-container status-danger">CRITICAL ALERT: DROWSINESS DETECTED</div>', 
                unsafe_allow_html=True
            )
            status_indicator.markdown("🔴 **CRITICAL**")
            alarm_placeholder.markdown(ALARM_AUDIO_HTML, unsafe_allow_html=True)
        else:
            metric_placeholder.markdown(
                f'<div class="metric-container status-safe">SYSTEM NORMAL<br>EAR: {current_ear:.2f}</div>', 
                unsafe_allow_html=True
            )
            status_indicator.markdown("🟢 **ONLINE**")
            alarm_placeholder.empty()

        time.sleep(0.1)
