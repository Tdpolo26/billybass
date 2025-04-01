# -*- coding: utf-8 -*-
import os
import time
import json
import threading
import pygame
import whisper
import subprocess
import RPi.GPIO as GPIO
from flask import Flask, request, render_template_string, redirect
from pydub import AudioSegment
from datetime import datetime
import numpy as np
from audio_analysis import load_all_files, convert_and_analyze_audio
from motor_control import pwm_motor, pulse_led
from settings import load_settings, save_settings, settings

# GPIO Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
NSLEEP1 = 12
NSLEEP2 = 13
MOUTH_IN1, MOUTH_IN2 = 17, 27
BODY_IN1, BODY_IN2 = 22, 23
TAIL_IN1, TAIL_IN2 = 24, 25
LED_PIN = 5

GPIO.setup([NSLEEP1, NSLEEP2, MOUTH_IN1, MOUTH_IN2, BODY_IN1, BODY_IN2,
            TAIL_IN1, TAIL_IN2, LED_PIN], GPIO.OUT)
GPIO.output(NSLEEP1, GPIO.HIGH)
GPIO.output(NSLEEP2, GPIO.HIGH)
GPIO.output(LED_PIN, GPIO.LOW)

# Init
app = Flask(__name__)
pygame.mixer.init()
whisper_model = whisper.load_model("tiny")

UPLOAD_FOLDER = "uploads"
SETTINGS_FILE = "settings.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

file_data = {}
playback_active = True
favorites = []

def load_timestamps(json_path):
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return []

# Main app route for upload and controls
@app.route("/", methods=["GET", "POST"])
def home():
    global playback_active
    if request.method == "POST":
        form = request.form
        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename:
                raw_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(raw_path)
                wav_path, json_path, duration = convert_and_analyze_audio(raw_path, UPLOAD_FOLDER)
                date = datetime.now().strftime("%Y-%m-%d %H:%M")
                timestamps = load_timestamps(json_path)
                file_data[wav_path] = {
                    "name": os.path.basename(wav_path),
                    "json": json_path,
                    "date": date,
                    "duration": duration,
                    "mouth": [t[0] for t in timestamps],
                    "body": [t[0] for t in timestamps[::3]],
                    "tail": [t[0] for t in timestamps[::4]],
                    "full": timestamps,
                    "waveform": generate_waveform(wav_path)
                }

        elif "play" in form:
            path = form["play"]
            play_audio_threaded(path, file_data[path]["json"])

        elif "pause" in form:
            playback_active = False
            pygame.mixer.music.stop()

        elif "volume" in form:
            settings["volume"] = float(form["volume"]) / 100.0
            save_settings()

        return redirect("/")

    sorted_files = sorted(file_data.items(), key=lambda x: x[1]["date"], reverse=True)

    return render_template_string('''
    <!doctype html>
    <html>
    <head>
        <title>Billy Bass</title>
        <style>
        /* Add your CSS here */
        </style>
    </head>
    <body>
        <div>
            <form method=post enctype=multipart/form-data>
                <input type=file name=file>
                <button type=submit>Upload</button>
            </form>
            <h2>Tracks</h2>
            {% for path, meta in files %}
            <div>
                <b>{{ meta.name }}</b> ({{ meta.duration }}s)
                <form method=post style="display:inline;">
                    <input type=hidden name=play value="{{ path }}">
                    <button type=submit>? Play</button>
                </form>
                <form method=post style="display:inline;">
                    <input type=hidden name=pause value="1">
                    <button type=submit>? Pause</button>
                </form>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    ''', files=sorted_files)


def play_audio_threaded(filepath, json_path):
    threading.Thread(target=play_audio_with_movement, args=(filepath, json_path), daemon=True).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
