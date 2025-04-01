import RPi.GPIO as GPIO
import time

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

# Motor control
def pwm_motor(in1, in2, duration, duty=100):
    freq = 1000
    pwm_channels = {}
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
