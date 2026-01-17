from faster_whisper import WhisperModel
from config.manager import config
from utils.logger import app_logger
import os

class TranscriptionEngine:
    def __init__(self):
        self._model = None
        self._current_config = {}
        self.reload_model()

    def reload_model(self):
        """Loads or reloads the Whisper model based on current config."""
        model_config = config.get("model", {})
        model_name = model_config.get("name", "base")
        device = model_config.get("device", "cpu")
        compute_type = model_config.get("compute_type", "int8")

        # Check if config actually changed to avoid unnecessary reloads
        new_config_sig = f"{model_name}-{device}-{compute_type}"
        current_config_sig = f"{self._current_config.get('name')}-{self._current_config.get('device')}-{self._current_config.get('compute_type')}"
        
        if self._model and new_config_sig == current_config_sig:
            return

        app_logger.info(f"Loading Whisper model: {model_name} on {device} ({compute_type})...")
        try:
            self._model = WhisperModel(model_name, device=device, compute_type=compute_type)
            self._current_config = model_config
            app_logger.info("Model loaded successfully.")
        except Exception as e:
            app_logger.error(f"Failed to load model: {e}")
            raise

    def transcribe(self, audio_path: str):
        if not self._model:
            self.reload_model()
        
        trans_config = config.get("transcription", {})
        # word_timestamps = trans_config.get("timestamp_granularity") == "word"
        
        segments, info = self._model.transcribe(
            audio_path, 
            beam_size=trans_config.get("beam_size", 5),
            language=trans_config.get("language"),
            # word_timestamps=word_timestamps 
            # Note: faster-whisper usage for word-level timestamps might need checking docs, 
            # usually word_timestamps=True returns words in segments.
            word_timestamps=True if trans_config.get("timestamp_granularity") == "word" else False
        )
        
        # segments is a generator, so we must iterate
        result_segments = []
        for segment in segments:
            result_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "words": segment.words if hasattr(segment, 'words') and segment.words else None
            })
            
        return {
            "segments": result_segments,
            "language": info.language,
            "duration": info.duration
        }

# Global engine instance
engine = TranscriptionEngine()
