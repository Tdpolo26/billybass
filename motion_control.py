# motion_control.py
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

MOTOR_PINS = {
    "mouth": (17, 27),
    "body": (22, 23),
    "tail": (24, 25)
}

NSLEEP1, NSLEEP2 = 12, 13
GPIO.setup([NSLEEP1, NSLEEP2] + [pin for pair in MOTOR_PINS.values() for pin in pair], GPIO.OUT)
GPIO.output(NSLEEP1, GPIO.HIGH)
GPIO.output(NSLEEP2, GPIO.HIGH)

pwm_channels = {}

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

def test_motor_route(motor, settings):
    if motor in MOTOR_PINS:
        in1, in2 = MOTOR_PINS[motor]
        pwm_motor(in1, in2, 0.3, settings["pwm"][motor])
    from flask import redirect
    return redirect("/")
