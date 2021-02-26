import RPi.GPIO as GPIO
import time

channel = 19
GPIO.setmode(GPIO.BCM)

GPIO.setup(channel,GPIO.OUT)
GPIO.output(channel,GPIO.LOW)

while(1):
        
    channel_is_on = GPIO.input(channel)

    if channel_is_on:
        print("ON")
    else:
        print("OFF")
    time.sleep(1)    