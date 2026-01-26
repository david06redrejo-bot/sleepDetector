# Neuro-Vigilance Sleep Detector

A real-time drowsiness detection system using Computer Vision and AI. Designed for local desktop execution.

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

## Overview

This project uses **MediaPipe Face Mesh** to detect facial landmarks and calculate the **Eye Aspect Ratio (EAR)**. If the user's eyes receive a closure score below a certain threshold for a consecutive number of frames, an audible alarm is triggered to wake the user.

## Features

- **Real-Time Monitoring**: Low-latency feed from the default webcam.
- **EAR Calculation**: Precise measurement of eye openness.
- **Audible Alarm**: Native system sound trigger when drowsiness is detected.
- **Visual Alerts**: On-screen warning text and bounding boxes.
- **Privacy First**: All processing happens locally on your machine. No video data is sent to the cloud.

## Requirements

- Python 3.8 or higher
- A webcam
- Windows OS (recommended for `winsound` support)

## Installation

1.  **Clone the repository** (if not already done):
    ```bash
    git clone <repository-url>
    cd CV-PER_PROJECT
    ```

2.  **Install Dependencies**:
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application**:
    ```bash
    python main.py
    ```

2.  **Operation**:
    - The application will open a window named `SleepDetector v1.0`.
    - Keep your face within the camera frame.
    - The real-time EAR value is displayed in the top-right corner.
    - **Test the alarm**: Close your eyes for about 3-5 seconds.

3.  **Exit**:
    - Press `Esc` key to close the application.

## Project Structure

```text
CV-PER_PROJECT/
├── assets/             # Audio files and static resources
├── guide/              # Lab guides and PDFs
├── models/             # MediaPipe task models
├── src/
│   ├── config.py       # Configuration settings
│   └── utils/
│       └── geometry.py # EAR calculation logic
├── main.py             # Application entry point
├── requirements.txt    # Project dependencies
└── README.md           # This file
```

## Configuration

You can adjust sensitivity settings in `src/config.py`:
- `EYE_ASPECT_RATIO_THRESHOLD`: EAR value below which eyes are considered closed (default: 0.25).
- `EYE_ASPECT_RATIO_CONSEC_FRAMES`: Number of consecutive frames to trigger alarm (default: 16).
