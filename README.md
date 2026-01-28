# Neuro-Vigilance Sleep Detector

A real-time drowsiness detection system using Computer Vision and AI.  
**Now migrated to Streamlit for easy web/cloud deployment (Hugging Face Spaces compatible).**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/SDK-Streamlit-FF4B4B)
![OpenCV](https://img.shields.io/badge/Computer_Vision-OpenCV-green)

## Overview

This project uses **MediaPipe Face Mesh** to detect facial landmarks and calculate the **Eye Aspect Ratio (EAR)**. If the user's eyes stay closed for a consecutive number of frames, the system triggers an alarm.

**Key Update**: The application now runs as a web app using **Streamlit WebRTC**. It processes video frames in real-time and injects client-side audio (`alarm.wav`) directly into the browser when drowsiness is detected.

## Features

- **Web-Based Interface**: Accessible via any modern browser using Streamlit.
- **Real-Time Monitoring**: Low-latency video processing via WebRTC.
- **EAR Calculation**: Precise measurement of eye openness.
- **Client-Side Audio**: Plays an alarm sound directly in the user's browser (bypassing server limitations).
- **Privacy First**: Video streams are processed in memory and never saved.

## Requirements

- Python 3.9 or higher
- A webcam
- `streamlit`, `streamlit-webrtc`, `opencv-python-headless`

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/david06redrejo-bot/sleepDetector.git
    cd sleepDetector
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application**:
    ```bash
    streamlit run main.py
    ```

2.  **Operation**:
    - A browser window will open.
    - Click **Start** to enable the webcam.
    - The real-time EAR value is displayed on the video feed.
    - **Test the alarm**: Close your eyes for about 3-5 seconds. The alarm will sound automatically.

## Deployment (Hugging Face Spaces)

This project is optimized for Hugging Face Spaces.
1. Create a **Streamlit** Space.
2. Upload the files (ensure `packages.txt` is included).
3. The app runs automatically.

## Project Structure

```text
sleepDetector/
├── assets/             # Audio files and static resources
├── models/             # MediaPipe task models
├── src/
│   ├── config.py       # Configuration settings
│   └── utils/
├── main.py             # Streamlit Application entry point
├── packages.txt        # System dependencies (Linux/Debian)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```
