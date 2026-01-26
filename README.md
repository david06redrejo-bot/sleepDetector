# Real-Time Drowsiness Detection System

## Overview
**SleepDetector** is a computer vision application designed to prevent driver drowsiness accidents. By leveraging the **MediaPipe Use Tasks API** for high-precision facial landmark detection, the system calculates the Eye Aspect Ratio (EAR) in real-time to monitor the user's eye state. If the eyes remain closed for a specific duration, an audible alarm is triggered.

This project demonstrates the practical application of geometric computer vision and real-time state estimation.

## Features
- **Real-Time Tracking**: 30+ FPS face mesh inference on standard CPU.
- **Robust Metrics**: Uses the Eye Aspect Ratio (EAR) metric for scale-invariant eye state estimation.
- **Temporal Filtering**: Implements a state machine to filter out normal blinking.
- **Audio Alerts**: Non-blocking asynchronous alarm system.

## Usage
1. **Installation**:
   ```bash
   pip install opencv-python mediapipe
   ```
2. **Run**:
   ```bash
   python main.py
   ```
3. **Calibration**:
   Adjust `EYE_ASPECT_RATIO_THRESHOLD` in `config.py` to match your lighting conditions.

## Technical Details
The core logic relies on the 6-point eye landmark model:
$$ EAR = \frac{||p_2 - p_6|| + ||p_3 - p_5||}{2 \times ||p_1 - p_4||} $$
This ratio remains constant when eyes are open but tends to zero as the eyelids close.

## Author
**David Redrejo**
Computer Vision Personal Project.
