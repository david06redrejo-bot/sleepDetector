"""
utils/alarm.py

Handles system alerts (Audio/Visual) for the Drowsiness Detection System.
"""

import winsound

def trigger_alarm():
    """
    Activates the drowsiness alarm in a non-blocking loop.
    """
    print("FOCUS! - DROWSINESS DETECTED")
    # SND_LOOP: Repeats the sound until purging
    # SND_ASYNC: Does not block the main video loop
    winsound.PlaySound("alarm.wav", winsound.SND_ASYNC | winsound.SND_FILENAME | winsound.SND_LOOP)

def deactivate_alarm():
    """
    Deactivates or resets the alarm state.
    """
    winsound.PlaySound(None, winsound.SND_PURGE)
