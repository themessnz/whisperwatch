import yaml
import os
from typing import Any, Dict
from utils.logger import app_logger

class ConfigManager:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            app_logger.warning(f"Config file not found at {self.config_path}. Using defaults.")
            return self._get_defaults()
        
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or self._get_defaults()
        except Exception as e:
            app_logger.error(f"Error loading config: {e}")
            return self._get_defaults()

    def _get_defaults(self) -> Dict[str, Any]:
        return {
            "watchKey": {
                "paths": ["/workspace/media"],
                "extensions": [".mp3", ".wav", ".mp4", ".mkv", ".mov", ".m4a"],
                "stability_check_seconds": 2
            },
            "model": {
                "name": "base",
                "device": "cpu",  # or cuda
                "compute_type": "int8" # float16, int8_float16
            },
            "transcription": {
                "language": None, # None = auto
                "beam_size": 5,
                "timestamp_granularity": "segment" # or word
            },
            "output": {
                "output_dir": "/workspace/transcripts",
                "formats": ["json", "txt", "srt", "vtt"]
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def update(self, new_config: Dict[str, Any]):
        self._config.update(new_config)
        self._save()

    def _save(self):
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self._config, f)
        except Exception as e:
            app_logger.error(f"Failed to save config: {e}")

config = ConfigManager()
