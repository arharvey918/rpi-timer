import RPi.GPIO as GPIO
import time
import math

from datetime import datetime
from datetime import timedelta

# Timer length in seconds
TIMER_LENGTH = 30

# GPIO constants
GREEN = 24
PROGRESS = [23, 5, 6, 16, 26]
BUTTON = 25

button_pressed = False
button_pressed_start = None

exit_signal = False
reset_signal = False
start_signal = False

interrupted = False

tick_pin = PROGRESS[0]

# Define a threaded callback function to run in another thread when events are detected


def button_callback(channel):
    global button_pressed_start, exit_signal, reset_signal, start_signal, interrupted, BUTTON

    if GPIO.input(BUTTON):     # if port 25 == 1
        print("Rising edge detected on 25")
        button_pressed_start = datetime.now()
    else:                  # if port 25 != 1
        print("Falling edge detected on 25")
        button_pressed_length = datetime.now() - button_pressed_start
        if button_pressed_length.seconds > 5:
            print("BUTTON: exit")
            exit_signal = True
            interrupted = True
        elif button_pressed_length.seconds > 2:
            print("BUTTON: reset/stop")
            reset_signal = True
            interrupted = True
        else:
            print("BUTTON: start")
            start_signal = True


def flicker():
    global PROGRESS
    for i in range(4):
        GPIO.output(PROGRESS[0], GPIO.HIGH)
        time.sleep(.1)
        GPIO.output(PROGRESS[0], GPIO.LOW)
        time.sleep(.1)


def tick():
    global tick_pin
    GPIO.output(tick_pin, GPIO.HIGH)
    time.sleep(.5)
    GPIO.output(tick_pin, GPIO.LOW)
    time.sleep(.5)


def in_progress():
    global GREEN, PROGRESS
    GPIO.output(GREEN, GPIO.LOW)
    flicker()

    for pin in PROGRESS:
        GPIO.output(pin, GPIO.HIGH)


def complete():
    global GREEN
    for pin in PROGRESS:
        GPIO.output(pin, GPIO.LOW)
    flicker()

    GPIO.output(GREEN, GPIO.HIGH)


def start_timer(seconds):
    global interrupted, tick_pin, PROGRESS
    counter = 0

    # Mark timer as in-progress
    in_progress()

    # Calculate start time
    start = datetime.now()

    # Calculate end time
    end = start + timedelta(seconds=seconds)

    # Set tick pin
    tick_pin = PROGRESS[len(PROGRESS) - 1]

    # Loop until we get to end
    while datetime.now() < end:
        tick()

        delta = end - datetime.now()

        if delta.days >= 0:
            pin_index = math.ceil(delta.seconds / float(seconds) * len(PROGRESS))
            pin_index = max(0, pin_index)

            # Set new tick pin
            print("pin index is %d" % pin_index)
            tick_pin = PROGRESS[pin_index]

        if interrupted:
            interrupted = False  # Clear the flag and exit            
            break

    complete()


if __name__ == "__main__":
    # Setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Set pin 25 to be an input pin and set initial value to be pulled low (off)
    GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.setup(GREEN, GPIO.OUT)
    for pin in PROGRESS:
        print ("Setting pin %d as output" % pin)
        GPIO.setup(pin, GPIO.OUT)

    # Setup event on pin 25 rising edge
    GPIO.add_event_detect(BUTTON, GPIO.BOTH, callback=button_callback)

    try:
        while True:
            # Main loop
            # Mark us as ready
            GPIO.output(GREEN, GPIO.HIGH)

            print("Press button to start timer")

            while not start_signal:
                time.sleep(.5)

            print("Timer started")
            start_timer(TIMER_LENGTH)

            # Reset these flags after the timer ends
            reset_signal = False
            start_signal = False

            if exit_signal:
                break
            else:
                print("Press button for 5 seconds to end program")


    finally:                   # this block will run no matter how the try block exits
        print("Cleaning up")
        for pin in PROGRESS:
            GPIO.output(pin, GPIO.LOW)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.cleanup()         # clean up after yourself
