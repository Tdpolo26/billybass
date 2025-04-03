import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
MOUTH_IN1, MOUTH_IN2 = 17, 27
GPIO.setup([MOUTH_IN1, MOUTH_IN2], GPIO.OUT)

p1 = GPIO.PWM(MOUTH_IN1, 1000)
p2 = GPIO.PWM(MOUTH_IN2, 1000)
p1.start(50)
p2.start(0)

time.sleep(1)

p1.ChangeDutyCycle(0)
p2.ChangeDutyCycle(0)
p1.stop()
p2.stop()
GPIO.cleanup()
