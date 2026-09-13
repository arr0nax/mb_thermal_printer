import RPi.GPIO as IO
import time

# Define the GPIO pin connected to the button
UP_BUTTON_PIN = 27
DOWN_BUTTON_PIN = 22
PRINT_BUTTON_PIN = 4
VANGUARD_BUTTON_PIN = 23

# Set the IO mode to BCM
IO.setmode(IO.BCM)

# Initialize the pushbutton pin as an input with a pull-up resistor
# The pull-up input pin will be HIGH when the switch is open and LOW when the switch is closed.
IO.setup(UP_BUTTON_PIN, IO.IN, pull_up_down=IO.PUD_UP)
IO.setup(DOWN_BUTTON_PIN, IO.IN, pull_up_down=IO.PUD_UP)
IO.setup(PRINT_BUTTON_PIN, IO.IN, pull_up_down=IO.PUD_UP)
IO.setup(VANGUARD_BUTTON_PIN, IO.IN, pull_up_down=IO.PUD_UP)

try:
    while True:
        # Read the state of the switch/button
        up_button_state = not IO.input(UP_BUTTON_PIN)
        down_button_state = not IO.input(DOWN_BUTTON_PIN)
        print_button_state = not IO.input(PRINT_BUTTON_PIN)
        vanguard_button_state = not IO.input(VANGUARD_BUTTON_PIN)

        if(up_button_state, down_button_state, print_button_state, vanguard_button_state):
            print("4 buttons")

        # Small delay to avoid unnecessary printing
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")
    # Clean up GPIO settings
    IO.cleanup()
