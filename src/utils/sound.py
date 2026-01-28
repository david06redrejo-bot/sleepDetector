"""
src/utils/sound.py

Handles system alerts (Audio/Visual) for the Drowsiness Detection System.
Refactored to play alarm.wav asynchronously on Windows.
"""

import os
import threading
import time
from src.config import ALARM_SOUND_PATH

try:
    import winsound
except ImportError:
    winsound = None

_ALARM_THREAD = None
_STOP_ALARM = False
_IS_PLAYING = False

def _fallback_loop():
    """Fallback loop for non-Windows systems or missing audio."""
    global _STOP_ALARM
    while not _STOP_ALARM:
        print('\a')  # System bell
        time.sleep(1)

def trigger_alarm():
    """
    Activates the drowsiness alarm.
    On Windows: Plays wav file in loop asynchronously.
    Others: Beeps in a thread.
    """
    global _ALARM_THREAD, _STOP_ALARM, _IS_PLAYING
    
    # Prevent re-triggering if already playing
    if _IS_PLAYING:
        return

    print("ALARM TRIGGERED: Drowsiness Detected!")
    _IS_PLAYING = True
    _STOP_ALARM = False

    # Windows Method
    if winsound and os.path.exists(ALARM_SOUND_PATH):
        try:
            # Play sound asynchronously and loop it
            # SND_FILENAME: File path is used
            # SND_LOOP: Loop the sound
            # SND_ASYNC: Do not block execution
            flags = winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC
            winsound.PlaySound(ALARM_SOUND_PATH, flags)
            return
        except Exception as e:
            print(f"[ERROR] Failed to play alarm sound: {e}")
            # Fall through to fallback
            
    # Fallback Method (Threaded Beep)
    if _ALARM_THREAD is None or not _ALARM_THREAD.is_alive():
        _ALARM_THREAD = threading.Thread(target=_fallback_loop, daemon=True)
        _ALARM_THREAD.start()

def deactivate_alarm():
    """
    Deactivates or resets the alarm state immediately.
    """
    global _ALARM_THREAD, _STOP_ALARM, _IS_PLAYING
    
    if not _IS_PLAYING:
        return

    print("ALARM DEACTIVATED: Alert condition resolved.")
    _IS_PLAYING = False
    _STOP_ALARM = True
    
    # Stop Windows Sound
    if winsound:
        try:
            # SND_PURGE stops all instances of specified sound, None stops currently playing
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception as e:
            print(f"[ERROR] Failed to stop sound: {e}")

    # The fallback thread will read _STOP_ALARM and exit naturally
    if _ALARM_THREAD is not None:
        _ALARM_THREAD = None
