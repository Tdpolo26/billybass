import os
import json
from pydub import AudioSegment
import whisper
import numpy as np

whisper_model = whisper.load_model("tiny")

def generate_waveform(path):
    audio = AudioSegment.from_wav(path)
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)
    downsampled = samples[::max(1, len(samples) // 300)]
    normalized = (downsampled - downsampled.min()) / (downsampled.ptp() + 1e-6)
    return normalized.tolist()

def load_timestamps(json_path):
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return []

def convert_and_analyze_audio(input_path, upload_folder):
    audio = AudioSegment.from_file(input_path).set_channels(1).normalize()
    if len(audio) < 500:
        raise Exception("Audio too short or empty")

    base = os.path.splitext(os.path.basename(input_path))[0]
    wav_path = os.path.join(upload_folder, base + "_converted.wav")
    json_path = os.path.join(upload_folder, base + "_converted.json")

    if not os.path.exists(wav_path) or not os.path.exists(json_path):
        audio.export(wav_path, format="wav")
        result = whisper_model.transcribe(wav_path, word_timestamps=True, language="en")
        if not result.get("segments"):
            raise Exception("No speech segments found")
        timestamps = [(word["start"], word["end"]) for seg in result["segments"] for word in seg.get("words", [])]
        with open(json_path, "w") as f:
            json.dump(timestamps, f)

    duration = round(audio.duration_seconds, 2)
    return wav_path, json_path, duration

def load_all_files(upload_folder):
    file_data = {}
    for file in os.listdir(upload_folder):
        if file.endswith("_converted.wav"):
            base = file[:-13]
            wav_path = os.path.join(upload_folder, file)
            json_path = os.path.join(upload_folder, base + "_converted.json")
            if not os.path.exists(json_path): continue
            timestamps = load_timestamps(json_path)
            waveform = generate_waveform(wav_path)
            duration = round(pygame.mixer.Sound(wav_path).get_length(), 2)
            date = datetime.fromtimestamp(os.path.getctime(wav_path)).strftime("%Y-%m-%d %H:%M")
            file_data[wav_path] = {
                "name": file,
                "json": json_path,
                "date": date,
                "duration": duration,
                "mouth": [t[0] for t in timestamps],
                "body": [t[0] for t in timestamps[::3]],
                "tail": [t[0] for t in timestamps[::4]],
                "full": timestamps,
                "waveform": waveform
            }
    return file_data
