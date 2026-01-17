import uvicorn
from api.main import app
from watcher.observer import WatcherService
from jobs.worker import start_worker
from utils.logger import app_logger
import contextlib

# Global service instances
watcher_service = WatcherService()
worker_thread = None

@contextlib.asynccontextmanager
async def lifespan(app):
    # Startup
    app_logger.info("Starting WhisperWatch services...")
    
    # Start Watcher
    watcher_service.start()
    
    # Start Worker
    # We keep a reference but threading.Thread object isn't easily "stopped" 
    # unless we implemented a stop flag in the loop (which we did implicitly with None check but we need to send it)
    global worker_thread
    worker_thread = start_worker()
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down WhisperWatch services...")
    watcher_service.stop()
    
    # In a real app we would signal the worker to stop cleanly
    # For now we rely on daemon=True in worker.py

# Assign lifespan to app (Monkey patch or re-init? Re-init is better but app is already creating in api/main)
# Better to do this in api/main.py or just import app here and assign lifespan.
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    uvicorn.run("service.bootstrap:app", host="0.0.0.0", port=8000, reload=False)
