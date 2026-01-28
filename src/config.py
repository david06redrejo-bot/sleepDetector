"""
src/config.py

Configuration constants for the Drowsiness Detection System.
Handles dynamic path resolution for assets and models.
"""

import os

# -----------------------------------------------------------------------------
# PATH CONFIGURATION
# -----------------------------------------------------------------------------
# Calculate the project root relative to this file
# Structure: sleep_detector/src/config.py
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

# -----------------------------------------------------------------------------
# EYE ASPECT RATIO (EAR) SETTINGS
# -----------------------------------------------------------------------------
EYE_ASPECT_RATIO_THRESHOLD = 0.20
EYE_ASPECT_RATIO_CONSEC_FRAMES = 14

# -----------------------------------------------------------------------------
# HARDWARE SETTINGS
# -----------------------------------------------------------------------------
WEBCAM_ID = 0
ALARM_SOUND_PATH = os.path.join(ASSETS_DIR, "alarm.wav")
