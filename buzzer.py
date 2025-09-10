"""
library that deals with all buzzer stuff
"""
import RPi.GPIO as GPIO


# GPIO Variables\Methods
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Warning and Buzzer Pins
pin_Ora = 36
pin_Red = 38
pin_Buz = 40
GPIO.setup(pin_Ora, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(pin_Red, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(pin_Buz, GPIO.OUT, initial = GPIO.HIGH)
# For DEMO
FLOOD_NO = 5
FLOOD_LOW = 10
FLOOD_HIGH = 20
FLOOD_TRIGGER = 0


def notify_buzzer(flood_height):
    pass
