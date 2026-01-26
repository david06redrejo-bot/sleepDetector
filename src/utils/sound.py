"""
src/utils/sound.py

Handles system alerts (Audio/Visual) for the Drowsiness Detection System.
Refactored for Cloud Deployment (Linux Compatible): Removed winsound dependency.
"""

import os
# from src.config import ALARM_SOUND_PATH # path unused in print-only version

def trigger_alarm():
    """
    Activates the drowsiness alarm.
    On server/cloud environments, sound playback via winsound is disabled.
    This function now just logs the event.
    """
    print("ALARM TRIGGERED: Drowsiness Detected! (Audio handled by client-side or suppressed)")

def deactivate_alarm():
    """
    Deactivates or resets the alarm state.
    """
    print("ALARM DEACTIVATED: Alert condition resolved.")
