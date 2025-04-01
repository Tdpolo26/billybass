# billy_bass.py
from flask import Flask, render_template, request, redirect
import pygame
import os
from app.settings import load_settings, save_settings
from app.audio_analysis import process_uploads, load_all_files
from app.motion_control import play_audio_threaded, test_motor_pwm
from app.tts import speak_text
from app.utils import ensure_upload_folder

app = Flask(__name__)
pygame.mixer.init()

UPLOAD_FOLDER = "uploads"
ensure_upload_folder(UPLOAD_FOLDER)
file_data = load_all_files(UPLOAD_FOLDER)
settings = load_settings()

@app.route("/", methods=["GET", "POST"])
def home():
    global file_data
    if request.method == "POST":
        form = request.form
        if "file" in request.files:
            f = request.files["file"]
            if f and f.filename:
                path, meta = process_uploads(f, UPLOAD_FOLDER)
                file_data[path] = meta
                return redirect("/")
        elif "play" in form:
            path = form["play"]
            play_audio_threaded(path, file_data[path]["json"])
        elif "pause" in form:
            pygame.mixer.music.stop()
        elif "volume" in form:
            settings["volume"] = float(form["volume"]) / 100.0
            save_settings(settings)
        elif "motor" in form:
            settings["pwm"][form["motor"]] = int(form["pwm"])
            save_settings(settings)
        elif "smoothing" in form:
            settings["smoothing"] = int(form["smoothing"])
            save_settings(settings)
        elif "text" in form:
            speak_text(form["text"])
        elif "delete" in form:
            path = form["delete"]
            try:
                os.remove(path)
                os.remove(file_data[path]["json"])
            except:
                pass
            file_data.pop(path, None)
        return redirect("/")

    sorted_files = sorted(file_data.items(), key=lambda x: x[1]["date"], reverse=True)
    return render_template("index.html",
                           files=sorted_files,
                           volume=settings["volume"],
                           pwm=settings["pwm"],
                           smoothing=settings["smoothing"])

@app.route("/test/<motor>", methods=["POST"])
def test_motor(motor):
    test_motor_pwm(motor)
    return redirect("/")

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    finally:
        pygame.mixer.quit()
