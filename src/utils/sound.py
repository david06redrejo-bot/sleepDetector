"""
src/utils/sound.py

Handles system alerts (Audio/Visual) for the Drowsiness Detection System.
"""

import winsound
import os
from src.config import ALARM_SOUND_PATH

def trigger_alarm():
    """
    Activates the drowsiness alarm in a non-blocking loop.
    Uses the path defined in config.py
    """
    print("FOCUS! - DROWSINESS DETECTED")
    winsound.PlaySound(ALARM_SOUND_PATH, winsound.SND_ASYNC | winsound.SND_FILENAME | winsound.SND_LOOP)

def deactivate_alarm():
    """
    Deactivates or resets the alarm state.
    """
    winsound.PlaySound(None, winsound.SND_PURGE)
