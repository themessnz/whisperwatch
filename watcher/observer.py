import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jobs.queue import job_manager
from utils.files import is_file_stable
from config.manager import config
from utils.logger import app_logger

class MediaHandler(FileSystemEventHandler):
    def __init__(self):
        self.processed = set()
        self.watch_config = config.get("watchKey", {})

    def on_created(self, event):
        if event.is_directory:
            return
        self._process_event(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self._process_event(event.dest_path)

    def _process_event(self, filepath):
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()
        
        allowed_exts = self.watch_config.get("extensions", [])
        if ext not in allowed_exts:
            return

        app_logger.info(f"New file detected: {filename}")
        
        # Debounce / Stability check
        wait_time = self.watch_config.get("stability_check_seconds", 2)
        if is_file_stable(filepath, wait_time):
             job_manager.create_job(filepath)
        else:
             app_logger.warning(f"File {filename} unstable or disappeared, skipping.")

class WatcherService:
    def __init__(self):
        self.observer = Observer()
        self.handler = MediaHandler()

    def start(self):
        paths = config.get("watchKey", {}).get("paths", [])
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)
                app_logger.info(f"Created watch directory: {path}")
            
            self.observer.schedule(self.handler, path, recursive=False)
            app_logger.info(f"Watching directory: {path}")
        
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
