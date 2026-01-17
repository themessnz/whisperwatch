import os
import json

def format_timestamp(seconds: float) -> str:
    """Formats seconds into HH:MM:SS,mmm for SRT"""
    milliseconds = int((seconds % 1) * 1000)
    minutes = int(seconds // 60)
    hours = minutes // 60
    minutes = minutes % 60
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def format_timestamp_vtt(seconds: float) -> str:
    """Formats seconds into HH:MM:SS.mmm for VTT"""
    milliseconds = int((seconds % 1) * 1000)
    minutes = int(seconds // 60)
    hours = minutes // 60
    minutes = minutes % 60
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

def save_transcript(result_data, output_dir, file_stem, formats):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    segments = result_data["segments"]

    if "json" in formats:
        with open(os.path.join(output_dir, f"{file_stem}.json"), 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

    if "txt" in formats:
        with open(os.path.join(output_dir, f"{file_stem}.txt"), 'w', encoding='utf-8') as f:
            for seg in segments:
                f.write(f"[{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}] {seg['text'].strip()}\n")

    if "srt" in formats:
        with open(os.path.join(output_dir, f"{file_stem}.srt"), 'w', encoding='utf-8') as f:
            for i, seg in enumerate(segments, 1):
                f.write(f"{i}\n")
                f.write(f"{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n")
                f.write(f"{seg['text'].strip()}\n\n")

    if "vtt" in formats:
        with open(os.path.join(output_dir, f"{file_stem}.vtt"), 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for seg in segments:
                f.write(f"{format_timestamp_vtt(seg['start'])} --> {format_timestamp_vtt(seg['end'])}\n")
                f.write(f"{seg['text'].strip()}\n\n")
