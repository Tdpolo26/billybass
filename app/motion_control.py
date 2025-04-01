import os
import json
import time
import threading
import pygame
import RPi.GPIO as GPIO
from app.settings import load_settings
settings = load_settings()

# Motor Pins
MOUTH_IN1, MOUTH_IN2 = 17, 27
BODY_IN1, BODY_IN2 = 22, 23
TAIL_IN1, TAIL_IN2 = 24, 25
LED_PIN = 5

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup([MOUTH_IN1, MOUTH_IN2, BODY_IN1, BODY_IN2, TAIL_IN1, TAIL_IN2, LED_PIN], GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

pwm_channels = {}
playback_active = True

def pwm_motor(in1, in2, duration, duty=100):
    freq = 1000
    if in1 not in pwm_channels:
        pwm_channels[in1] = GPIO.PWM(in1, freq)
        pwm_channels[in1].start(0)
    if in2 not in pwm_channels:
        pwm_channels[in2] = GPIO.PWM(in2, freq)
        pwm_channels[in2].start(0)
    pwm_channels[in1].ChangeDutyCycle(duty)
    pwm_channels[in2].ChangeDutyCycle(0)
    time.sleep(duration)
    pwm_channels[in1].ChangeDutyCycle(0)
    pwm_channels[in2].ChangeDutyCycle(0)

def pulse_led(duration=0.05):
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(LED_PIN, GPIO.LOW)

def move_mouth(timestamps):
    global playback_active
    idx = 0
    while pygame.mixer.music.get_pos() <= 0:
        time.sleep(0.01)
    while playback_active and pygame.mixer.music.get_busy():
        now = pygame.mixer.music.get_pos() / 1000.0
        if idx < len(timestamps) and now >= timestamps[idx][0]:
            start, end = timestamps[idx]
            duration = max(0.1, end - start)
            pwm_motor(MOUTH_IN1, MOUTH_IN2, duration, settings["pwm"]["mouth"])
            pulse_led()
            idx += 1
        time.sleep(0.005)

def sway_body(spans):
    global playback_active
    smoothing = max(1, settings.get("smoothing", 5))
    for start, end in spans:
        while pygame.mixer.music.get_pos() / 1000.0 < start:
            if not playback_active: return
            time.sleep(0.01)
        total_time = end - start
        step_duration = total_time / (2 * smoothing)
        for _ in range(smoothing):
            if not playback_active: return
            pwm_motor(BODY_IN1, BODY_IN2, 0.1, settings["pwm"]["body"])
            time.sleep(step_duration)
        for _ in range(smoothing):
            if not playback_active: return
            pwm_motor(BODY_IN2, BODY_IN1, 0.1, settings["pwm"]["body"])
            time.sleep(step_duration)

def tail_metronome(duration):
    global playback_active
    interval = 0.75
    elapsed = 0
    while playback_active and elapsed < duration:
        pwm_motor(TAIL_IN1, TAIL_IN2, 0.15, settings["pwm"]["tail"])
        pulse_led(0.05)
        time.sleep(interval)
        elapsed += interval

def group_spans(timestamps, gap=1.5):
    if not timestamps: return []
    spans = []
    current_start = timestamps[0][0]
    current_end = timestamps[0][1]
    for start, end in timestamps[1:]:
        if start - current_end <= gap:
            current_end = end
        else:
            spans.append((current_start, current_end))
            current_start = start
            current_end = end
    spans.append((current_start, current_end))
    return spans

def play_audio_with_movement(audio_path, timestamp_path):
    global playback_active
    playback_active = True

    if not os.path.exists(audio_path) or not os.path.exists(timestamp_path):
        return

    with open(timestamp_path, "r") as f:
        timestamps = json.load(f)

    spans = group_spans(timestamps)
    duration = pygame.mixer.Sound(audio_path).get_length()

    pygame.mixer.music.set_volume(settings["volume"])
    pygame.mixer.music.load(audio_path)

    threading.Thread(target=move_mouth, args=(timestamps,), daemon=True).start()
    threading.Thread(target=tail_metronome, args=(duration,), daemon=True).start()
    threading.Thread(target=sway_body, args=(spans,), daemon=True).start()

    time.sleep(0.1)
    pygame.mixer.music.play()

def play_audio_threaded(audio_path, timestamp_path):
    threading.Thread(target=play_audio_with_movement, args=(audio_path, timestamp_path), daemon=True).start()

def test_motor_pwm(motor):
    pin_map = {
        "mouth": (MOUTH_IN1, MOUTH_IN2),
        "body": (BODY_IN1, BODY_IN2),
        "tail": (TAIL_IN1, TAIL_IN2),
    }
    if motor in pin_map:
        pwm_motor(pin_map[motor][0], pin_map[motor][1], 0.3, settings["pwm"][motor])
