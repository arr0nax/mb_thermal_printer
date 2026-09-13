import RPi.GPIO as IO
import time

# Define the GPIO pin connected to the button
UP_BUTTON_PIN = 27
DOWN_BUTTON_PIN = 22

# Set the IO mode to BCM
IO.setmode(IO.BCM)

# Initialize the pushbutton pin as an input with a pull-up resistor
# The pull-up input pin will be HIGH when the switch is open and LOW when the switch is closed.
IO.setup(UP_BUTTON_PIN, IO.IN, pull_up_down=IO.PUD_UP)
IO.setup(DOWN_BUTTON_PIN, IO.IN, pull_up_down=IO.PUD_UP)

a = 13
b = 26
c = 20
d = 16
e = 12
f = 6
g = 5
h = 21

count = 0

DISPLAY = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x67]            # string of characters storing PORT values for each digit.
IO.setwarnings(False)            # do not show any warnings
IO.setup(a,IO.OUT)             # initialize GPIO Pins as outputs
IO.setup(b,IO.OUT)
IO.setup(c,IO.OUT)
IO.setup(d,IO.OUT)
IO.setup(e,IO.OUT)
IO.setup(f,IO.OUT)
IO.setup(g,IO.OUT)
IO.setup(h,IO.OUT)
def PORT(pin):                    # assigning GPIO logic by taking 'pin' value
    if(pin&0x01 == 0x01):
        IO.output(a,1)            # if  bit0 of 8bit 'pin' is true, pull PINa high
    else:
        IO.output(a,0)            # if  bit0 of 8bit 'pin' is false, pull PINa low
    if(pin&0x02 == 0x02):
        IO.output(b,1)             # if  bit1 of 8bit 'pin' is true, pull PIN6 high
    else:
        IO.output(b,0)            #if  bit1 of 8bit 'pin' is false, pull PIN6 low
    if(pin&0x04 == 0x04):
        IO.output(c,1)
    else:
        IO.output(c,0)
    if(pin&0x08 == 0x08):
        IO.output(d,1)
    else:
        IO.output(d,0)   
    if(pin&0x10 == 0x10):
        IO.output(e,1)
    else:
        IO.output(e,0)
    if(pin&0x20 == 0x20):
        IO.output(f,1)
    else:
        IO.output(f,0)
    if(pin&0x40 == 0x40):
        IO.output(g,1)
    else:
        IO.output(g,0)
    if(pin&0x80 == 0x80):
        IO.output(h,1)            # if  bit7 of 8bit 'pin' is true, pull PINh high
    else:
        IO.output(h,0)            # if  bit7 of 8bit 'pin' is false, pull PINh low
try:
    while True:
        # Read the state of the switch/button
        up_button_state = not IO.input(UP_BUTTON_PIN)
        down_button_state = not IO.input(DOWN_BUTTON_PIN)

        if(up_button_state):
            count += 1
            count = count % 10
            time.sleep(0.2)

        if(down_button_state):
            count += 9
            count = count % 10
            time.sleep(0.2)

        pin = DISPLAY[count]        # assigning value to 'pin' for each digit
        PORT(pin);                  # showing each digit on display 

        # Small delay to avoid unnecessary printing
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")
    # Clean up IO settings
    IO.cleanup()
