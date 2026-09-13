import RPi.GPIO as IO            # calling for header file which helps us use GPIO’s of PI
import time                              # calling for time to provide delays in program

a = 13
b = 26
c = 20
d = 16
e = 12
f = 6
g = 5
h = 21

DISPLAY = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x67]            # string of characters storing PORT values for each digit.
IO.setwarnings(False)            # do not show any warnings
IO.setmode (IO.BCM)           # programming the GPIO by BCM pin numbers. (like PIN29 as‘GPIO5’)
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
    while 1:
        for x in range(10):            # execute the loop ten times incrementing x value from zero to nine
            pin = DISPLAY[x]        # assigning value to 'pin' for each digit
            PORT(pin);                  # showing each digit on display 
            time.sleep(1)
except KeyboardInterrupt:
    print("\nExiting...")
    # Clean up GPIO settings
    IO.cleanup()
