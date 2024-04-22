import RPi.GPIO as GPIO
import time

def button_press(channel):
    print("Press: {}".format(channel))
    if channel == 6:
        print("RPi info: model:{}; RAM:{}".format(GPIO.RPI_INFO["TYPE"], GPIO.RPI_INFO["RAM"]))

DEBOUNCE = 500

GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(13, GPIO.RISING, callback=button_press, bouncetime=DEBOUNCE)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(6, GPIO.RISING, callback=button_press, bouncetime=DEBOUNCE)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(12, GPIO.RISING, callback=button_press, bouncetime=DEBOUNCE)

if GPIO.input(12) == 0:
    print("Auto start shunt on GPIO 12 detected. Auto start disabled.")


while True:
    GPIO.output(5, GPIO.LOW)
    time.sleep(1.5)
    GPIO.output(5, GPIO.HIGH)
    time.sleep(1.5)
