# Real-Time Drowsiness Detection System

## Overview
**Neuro-Vigilance** (formerly SleepDetector) is a dual-mode computer vision application designed to prevent driver drowsiness accidents. It leverages the **MediaPipe Tasks API** for high-precision facial landmark detection, calculating the Eye Aspect Ratio (EAR) to monitor alertness in real-time.

## Features
- **Dual Interface**:
    - **Web App**: Futuristic "Cyberpunk" UI via Streamlit (Browser-based).
    - **Desktop**: Lightweight OpenCV implementation.
- **Robust Metrics**: Uses EAR (Eye Aspect Ratio) for scale-invariant drowsy detection.
- **Client-Side Audio**: Web version uses HTML5 injection for browser-safe alerts.
- **Professional Architecture**: Structured package layout (`src/`) with dynamic path resolution.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/david06redrejo-bot/sleepDetector.git
   cd sleepDetector
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 🚀 Web Application (Recommended)
Launch the modern Cyberpunk dashboard:
```bash
streamlit run app.py
```
*Access via browser at `http://localhost:8501`*

### 💻 Desktop Version (Legacy)
Run the classic OpenCV window:
```bash
python main.py
```

## Configuration
Adjust system parameters in `src/config.py`:
- `EYE_ASPECT_RATIO_THRESHOLD` (Default: 0.25)
- `EYE_ASPECT_RATIO_CONSEC_FRAMES` (Default: 16)

## Project Structure
```text
sleep_detector/
├── app.py                 # Streamlit Web App Entry Point
├── main.py                # Desktop App Entry Point
├── assets/                # Static assets (CSS, Audio)
├── models/                # MediaPipe Model Bundles
└── src/                   # Source Code
    ├── config.py          # Dynamic Configuration
    ├── core/              # Logic & Inference
    └── utils/             # Helper Functions
```

## Technical Details
$$ EAR = \frac{||p_2 - p_6|| + ||p_3 - p_5||}{2 \times ||p_1 - p_4||} $$

## Author
**David Redrejo**
Computer Vision Personal Project.
