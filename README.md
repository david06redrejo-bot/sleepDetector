---
title: Drowsiness Detector
emoji: 😴
colorFrom: blue
colorTo: red
sdk: streamlit
sdk_version: 1.41.1
python_version: "3.10"
app_file: main.py
pinned: false
---

# 🧠 NeuroVigilance — Drowsiness Detection System

A real-time drowsiness detection system using Computer Vision and AI.  
**Premium safety monitoring dashboard with WebRTC streaming.**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Hugging_Face-yellow?style=for-the-badge)](https://huggingface.co/spaces/david06redrejo-bot/drowsiness-detector)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/SDK-Streamlit-FF4B4B)
![OpenCV](https://img.shields.io/badge/Computer_Vision-OpenCV-green)
![MediaPipe](https://img.shields.io/badge/AI-MediaPipe-orange)

---

## 🎯 Overview

This project uses **MediaPipe Face Mesh** to detect facial landmarks and calculate the **Eye Aspect Ratio (EAR)**. If the user's eyes stay closed for a consecutive number of frames, the system triggers an audio alarm.

### ✨ Key Features

- **Real-Time Monitoring** — Low-latency video processing
- **Premium UI** — Glassmorphism design with micro-animations
- **Web & Desktop** — Run locally or deploy to the cloud
- **Robust Connectivity** — STUN + TURN servers for reliable WebRTC
- **Privacy First** — Video is processed in memory, never saved

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Webcam
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/david06redrejo-bot/sleepDetector.git
cd sleepDetector

# Install dependencies
pip install -r requirements.txt
```

---

## 💻 Running the Application

### Option 1: 🌐 **Live Demo (No Installation)**

Try it instantly on Hugging Face:

👉 **[https://huggingface.co/spaces/david06redrejo-bot/drowsiness-detector](https://huggingface.co/spaces/david06redrejo-bot/drowsiness-detector)**

---

### Option 2: 🖥️ **Local Debug Mode (Desktop App)**

Best for development and testing with minimal latency.

```bash
python local_debug.py
```

**Features:**
- Uses OpenCV window (no browser needed)
- Direct webcam access
- Server-side audio playback (pygame)
- Fastest response time

**Controls:**
- Press `Q` to quit

---

### Option 3: 🌍 **Streamlit Web App (Local Server)**

Run the full web interface locally.

```bash
streamlit run main.py
```

**Features:**
- Full premium UI with glassmorphism design
- WebRTC video streaming
- Browser-based audio alerts
- Same experience as Hugging Face, but on your machine

**After running:**
1. Browser opens automatically at `http://localhost:8501`
2. Click **START** to enable camera
3. Grant camera permissions when prompted
4. Close your eyes for ~3 seconds to trigger the alarm

---

## ⚙️ Configuration

Detection parameters can be adjusted in `src/config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EYE_ASPECT_RATIO_THRESHOLD` | 0.20 | EAR below this = eyes closed |
| `EYE_ASPECT_RATIO_CONSEC_FRAMES` | 12 | Frames before alarm triggers |

---

## 📁 Project Structure

```text
sleepDetector/
├── assets/
│   ├── alarm.wav          # Alarm sound file
│   └── style.css          # Premium UI styles
├── models/
│   └── face_landmarker.task   # MediaPipe model
├── src/
│   ├── config.py          # Detection parameters
│   ├── rtc_config.py      # WebRTC STUN/TURN settings
│   └── utils/
│       ├── geometry.py    # EAR calculation
│       └── sound.py       # Audio handling
├── guide/
│   ├── WEBRTC_CONFIGURATION.md
│   └── HUGGING_FACE_DEPLOYMENT.md
├── main.py                # Streamlit web app
├── local_debug.py         # Desktop OpenCV app
├── requirements.txt       # Python dependencies
├── packages.txt           # System dependencies (Linux)
└── README.md
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Face Detection** | MediaPipe Face Landmarker |
| **Computer Vision** | OpenCV |
| **Web Framework** | Streamlit |
| **Video Streaming** | WebRTC (streamlit-webrtc) |
| **Audio** | Pygame (local) / HTML5 Audio (web) |
| **Deployment** | Hugging Face Spaces |

---

## 📊 How It Works

```
1. Webcam captures video frames
           ↓
2. MediaPipe detects face landmarks
           ↓
3. Calculate Eye Aspect Ratio (EAR)
           ↓
4. EAR < threshold for N consecutive frames?
           ↓
   YES → 🔊 TRIGGER ALARM
   NO  → Continue monitoring
```

---

## 📝 License

MIT License — Feel free to use and modify!

---

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) — Face landmark detection
- [Streamlit](https://streamlit.io/) — Web framework
- [Metered.ca](https://www.metered.ca/) — Free TURN servers

---

<p align="center">
  <b>Built for safety • Real-time AI monitoring</b><br>
  🧠 NeuroVigilance
</p>
