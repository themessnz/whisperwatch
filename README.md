# WhisperWatch

An offline video/audio transcription service using `faster-whisper`.

## Features

- **Watch Folders**: Automatically detects and processes new media files.
- **FastAPI Backend**: REST API for job management and configuration.
- **Web Dashboard**: View active jobs, history, and change settings.
- **Multiple Formats**: Outputs JSON, TXT, SRT, and VTT with timestamps.
- **Configurable**: Change Whisper models (tiny -> large-v3), devices (CPU/GPU), and more at runtime.

## Installation

### Docker (Recommended)

1. Build and run:
   ```bash
   docker-compose up --build -d
   ```
2. Access the UI at `http://localhost:8000`.
3. Place media files in the `./media` directory. Transcripts will appear in `./transcripts`.

### Manual (Linux)

1. Install requirements:
   ```bash
   apt-get install ffmpeg
   pip install -r requirements.txt
   ```
2. Run the service:
   ```bash
   python main.py
   ```

## Configuration

Configuration is stored in `config/config.yaml`. You can also modify settings via the Web UI at `http://localhost:8000/settings`.

- **Model**: Select from tiny, base, small, medium, large-v3.
- **Compute Type**: `int8` (fastest), `float16` (higher accuracy).
- **Device**: `cpu` or `cuda` (requires NVIDIA GPU).

## Architecture

- `watcher/`: Handles directory monitoring.
- `jobs/`: Background job queue and worker threads.
- `transcription/`: Whisper engine wrapper.
- `api/`: FastAPI routes.
- `ui/`: Dashboard templates.
- `storage/`: SQLite database for job tracking.

## License

MIT
