import subprocess

def speak_text(text):
    subprocess.call(["espeak", "-ven+f3", "-s150", text])
