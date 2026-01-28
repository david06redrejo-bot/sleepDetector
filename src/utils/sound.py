"""
src/utils/sound.py

Handles system alerts (Audio/Visual) for the Drowsiness Detection System.
Refactored for Cloud Deployment (Linux Compatible): Removed winsound dependency.
"""

import os
# from src.config import ALARM_SOUND_PATH # path unused in print-only version

import platform
import threading
import time

try:
    import winsound
except ImportError:
    winsound = None

from src.config import ALARM_SOUND_PATH

_ALARM_THREAD = None
_STOP_ALARM = False

def _play_loop():
    global _STOP_ALARM
    while not _STOP_ALARM:
        if winsound:
            # winsound.SND_FILENAME | winsound.SND_ASYNC stops the loop logic if not careful, 
            # so we use synchronous play in a thread or simple beep.
            # Using Beep for simplicity and reliability across Windows versions without wav file issues
            winsound.Beep(1000, 500) 
        else:
            # Linux/Mac fallback (print or use os.system)
            print('\a') # system bell
            time.sleep(0.5)

def trigger_alarm():
    """
    Activates the drowsiness alarm.
    Uses threading to prevent blocking the main video loop.
    """
    global _ALARM_THREAD, _STOP_ALARM
    
    if _ALARM_THREAD is None or not _ALARM_THREAD.is_alive():
        print("ALARM TRIGGERED: Drowsiness Detected!")
        _STOP_ALARM = False
        _ALARM_THREAD = threading.Thread(target=_play_loop, daemon=True)
        _ALARM_THREAD.start()

def deactivate_alarm():
    """
    Deactivates or resets the alarm state.
    """
    global _ALARM_THREAD, _STOP_ALARM
    
    if _ALARM_THREAD is not None:
        _STOP_ALARM = True
        _ALARM_THREAD = None
        print("ALARM DEACTIVATED: Alert condition resolved.")
