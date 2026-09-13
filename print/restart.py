import RPi.GPIO as GPIO
import time
import subprocess

# Define the GPIO pin connected to the button
BUTTON_PIN = 25

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Initialize the pushbutton pin as an input with a pull-up resistor
# The pull-up input pin will be HIGH when the switch is open and LOW when the switch is closed.
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # Read the state of the switch/button
        button_state = not GPIO.input(BUTTON_PIN)
        if (button_state):
            subprocess.run(["systemctl", "restart", "momir"])


        # Small delay to avoid unnecessary printing
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")
    # Clean up GPIO settings
    GPIO.cleanup()
