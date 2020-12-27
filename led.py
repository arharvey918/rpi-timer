import RPi.GPIO as GPIO
import time

reset_pressed = False

# Define a threaded callback function to run in another thread when events are detected  
def button_callback(channel):
    global reset_pressed

    if GPIO.input(25):     # if port 25 == 1  
        print("Rising edge detected on 25")
        reset_pressed = True
    else:                  # if port 25 != 1  
        print("Falling edge detected on 25")  

# Setup

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 25 to be an input pin and set initial value to be pulled low (off)

GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)

GPIO.add_event_detect(25,GPIO.BOTH,callback=button_callback) # Setup event on pin 25 rising edge

# Main loop
print("Main loop starting")

try:
    while not reset_pressed:
        time.sleep(.1)
    
    print("Continuing")
    GPIO.output(24,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(24,GPIO.LOW)

    GPIO.output(23,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(23,GPIO.LOW)  

finally:                   # this block will run no matter how the try block exits  
    print("Cleaning up")
    GPIO.cleanup()         # clean up after yourself  
