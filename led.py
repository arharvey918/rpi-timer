import RPi.GPIO as GPIO
import time

from datetime import datetime
from datetime import timedelta

# Timer length in seconds
TIMER_LENGTH = 10

button_pressed = False

# Define a threaded callback function to run in another thread when events are detected


def button_callback(channel):
    global button_pressed

    if GPIO.input(25):     # if port 25 == 1
        print("Rising edge detected on 25")
        button_pressed = True
    else:                  # if port 25 != 1
        print("Falling edge detected on 25")


def flicker():
    for i in range(4):
        GPIO.output(23, GPIO.HIGH)
        time.sleep(.1)
        GPIO.output(23, GPIO.LOW)
        time.sleep(.1)


def tick():
    GPIO.output(23, GPIO.HIGH)
    time.sleep(.5)
    GPIO.output(23, GPIO.LOW)
    time.sleep(.5)


def in_progress():
    flicker()
    GPIO.output(24, GPIO.LOW)


def complete():
    flicker()
    GPIO.output(24, GPIO.HIGH)


def start_timer(seconds):
    # Mark timer as in-progress
    in_progress()

    # Calculate start time
    start = datetime.now()

    # Calculate end time
    end = start + timedelta(seconds=seconds)

    # Loop until we get to end
    while datetime.now() < end:
        tick()

    complete()


if __name__ == "__main__":
    # Setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Set pin 25 to be an input pin and set initial value to be pulled low (off)
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.setup(23, GPIO.OUT)
    GPIO.setup(24, GPIO.OUT)

    # Setup event on pin 25 rising edge
    GPIO.add_event_detect(25, GPIO.BOTH, callback=button_callback)

    # Main loop
    print("Press button to start timer")

    # Mark us as ready
    GPIO.output(24, GPIO.HIGH)

    try:
        while not button_pressed:
            time.sleep(.1)

        button_pressed = False
        print("Continuing")
        start_timer(TIMER_LENGTH)

        print("Press button to stop program")
        while not button_pressed:
            time.sleep(1)

    finally:                   # this block will run no matter how the try block exits
        print("Cleaning up")
        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.cleanup()         # clean up after yourself
