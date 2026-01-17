import os
import time

def is_file_stable(filepath: str, wait_time: int = 2) -> bool:
    """Checks if a file size is constant over a short period."""
    if not os.path.exists(filepath):
        return False
        
    initial_size = os.path.getsize(filepath)
    time.sleep(wait_time)
    
    if not os.path.exists(filepath):
        return False
        
    final_size = os.path.getsize(filepath)
    return initial_size == final_size and final_size > 0

def get_mime_group(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']:
        return 'video'
    if ext in ['.mp3', '.wav', '.aac', '.flac', '.m4a', '.ogg', '.opus']:
        return 'audio'
    return 'unknown'
