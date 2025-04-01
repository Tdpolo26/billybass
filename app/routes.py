# routes.py

import os
from flask import request, redirect, render_template
from . import app
from .settings import settings, save_settings
from .audio_analysis import convert_and_analyze_audio, load_all_files, file_data
from .motion_control import test_motor, play_audio_threaded

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        form = request.form

        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename:
                raw_path = os.path.join("uploads", file.filename)
                file.save(raw_path)
                convert_and_analyze_audio(raw_path)
                load_all_files()

        elif "play" in form:
            path = form["play"]
            if path in file_data:
                play_audio_threaded(path, file_data[path]["json"])

        elif "pause" in form:
            from .motion_control import stop_playback
            stop_playback()

        elif "volume" in form:
            settings["volume"] = float(form["volume"]) / 100.0
            save_settings()

        elif "motor" in form:
            motor = form["motor"]
            pwm_value = int(form["pwm"])
            settings["pwm"][motor] = pwm_value
            save_settings()

        elif "smoothing" in form:
            settings["smoothing"] = int(form["smoothing"])
            save_settings()

        elif "text" in form:
            from .motion_control import speak_text
            speak_text(form["text"])

        elif "delete" in form:
            path = form["delete"]
            if path in file_data:
                try:
                    os.remove(path)
                    os.remove(file_data[path]["json"])
                except:
                    pass
                del file_data[path]

        elif "position" in form:
            from .motion_control import move_motor_to_position
            move_motor_to_position(form["position_motor"], int(form["position_value"]))

        return redirect("/")

    sorted_files = sorted(file_data.items(), key=lambda x: x[1]["date"], reverse=True)
    return render_template("index.html", files=sorted_files, volume=settings["volume"],
                           pwm=settings["pwm"], smoothing=settings["smoothing"])
