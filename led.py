import RPi.GPIO as GPIO
import time

from datetime import datetime
from datetime import timedelta

# Timer length in seconds
TIMER_LENGTH = 10

button_pressed = False
button_pressed_start = None


exit_signal = False
reset_signal = False
start_signal = False

interrupted = False

# Define a threaded callback function to run in another thread when events are detected


def button_callback(channel):
    global button_pressed_start, exit_signal, reset_signal, start_signal, interrupted

    if GPIO.input(25):     # if port 25 == 1
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
    GPIO.output(24, GPIO.LOW)
    flicker()


def complete():
    flicker()
    GPIO.output(24, GPIO.HIGH)


def start_timer(seconds):
    global interrupted

    # Mark timer as in-progress
    in_progress()

    # Calculate start time
    start = datetime.now()

    # Calculate end time
    end = start + timedelta(seconds=seconds)

    # Loop until we get to end
    while datetime.now() < end:
        tick()

        if interrupted:
            interrupted = False  # Clear the flag and exit            
            break

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

    try:
        while True:
            # Main loop
            # Mark us as ready
            GPIO.output(24, GPIO.HIGH)

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
        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.cleanup()         # clean up after yourself
