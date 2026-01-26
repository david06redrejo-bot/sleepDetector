"""
config.py

Configuration constants for the Drowsiness Detection System.
This file contains all tunable hyperparameters and system settings.
"""

# -----------------------------------------------------------------------------
# EYE ASPECT RATIO (EAR) SETTINGS
# -----------------------------------------------------------------------------
# Threshold: If EAR drops below this value, the eye is considered closed.
# Range: 0.20 - 0.30 (Calibrate based on camera/lighting).
EYE_ASPECT_RATIO_THRESHOLD = 0.25

# Temporal Threshold: Number of consecutive frames the eye must be closed
# to trigger an alarm. At 30 FPS, 16 frames is approx 0.5 seconds.
EYE_ASPECT_RATIO_CONSEC_FRAMES = 16

# -----------------------------------------------------------------------------
# HARDWARE SETTINGS
# -----------------------------------------------------------------------------
# Camera Index (0 = Default Webcam, 1 = External).
WEBCAM_ID = 0

# Path to the alert sound file.
ALARM_SOUND_PATH = "alarm.wav"
