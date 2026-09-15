import json, logging, os, random, sys, textwrap, time, unicodedata

logging.getLogger('escpos').setLevel(logging.WARNING)
logging.getLogger('serial').setLevel(logging.WARNING)

import RPi.GPIO as IO
from escpos.printer import Serial
from escpos.constants import GS
from escpos.image import EscposImage
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ART_ROOT = os.path.join(BASE_DIR, 'art')
CARDS_FILE = os.path.join(BASE_DIR, 'cards.json')
LINE_WIDTH = 32  # characters per line at the printer's default font 'a' size
TEXT_REPLACEMENTS = str.maketrans({
    '—': '-',
    '–': '-',
    '•': '*',
})

with open(CARDS_FILE, 'r', encoding='utf-8') as f:
    CARDS_BY_ID = {card['id']: card for card in json.load(f)}

p = Serial(devfile='/dev/serial0', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1.00, dsrdtr=False, xonxoff=True) #initilize thermal printer serial 
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

a = 13
b = 26
c = 20
d = 16
e = 12
f = 6
g = 5
h = 21

count = 0

DISPLAY = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x67, 0xBF, 0x86, 0xDB, 0xCF, 0xE6, 0xED, 0xFD]            # string of characters storing PORT values for each digit.
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

def format_printer_text(text):
    text = text.translate(TEXT_REPLACEMENTS)
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def front_face_text(text):
    return text.split(' // ', 1)[0]

def print_wrapped_text(text, width=LINE_WIDTH):
    text = format_printer_text(text)
    for paragraph in text.splitlines():
        if not paragraph:
            p.textln("")
            continue

        for line in textwrap.wrap(paragraph, width=width):
            p.textln(line)

def format_type_line(type_line):
    return format_printer_text(type_line)

def print_image_paced(image, chunk_size=256, delay=0.2):
    # No flow-control wiring to the printer (TX+GND only), so a full-speed burst
    # can overflow its buffer and drop bytes, shearing the image diagonally.
    # Trickle the raster payload instead of sending it in one write.
    im = EscposImage(image)
    header = (
        GS + b'v0' + bytes((0,))
        + p._int_low_high(im.width_bytes, 2)
        + p._int_low_high(im.height, 2)
    )
    p._raw(header)
    data = im.to_raster_format()
    for i in range(0, len(data), chunk_size):
        p._raw(data[i:i + chunk_size])
        time.sleep(delay)

def print_random_card(cmc): #function to print a card's text and art
    path = os.path.join(ART_ROOT, str(cmc), 'converted_files')
    try:
        # Resync the printer in case a previous job left its parser mid-command
        p.hw('INIT')
        art_file = random.choice(os.listdir(path))
        card_id = os.path.splitext(art_file)[0]
        card = CARDS_BY_ID.get(card_id)
        if not card:
            print(f"No card data found for {card_id}")
            return

        p.set(align='left', bold=True, custom_size=True, width=2, height=2)
        card_name = format_printer_text(front_face_text(card['name']))
        mana_cost = format_printer_text(front_face_text(card.get('mana_cost') or ''))
        header_width = LINE_WIDTH // 2
        padding = header_width - len(card_name) - len(mana_cost)
        header = card_name + (' ' * padding if padding > 0 else '') + mana_cost
        p.textln(header)
        p.textln("")

        p.set(align='center')
        with Image.open(os.path.join(path, art_file)) as art:
            half_size = (art.width // 2, art.height // 2)
            try:
                print_image_paced(art.resize(half_size))
            except Exception as image_error:
                # Image send failed/glitched - resync so the corruption doesn't
                # bleed into the text printed below.
                print("Image print failed, skipping image:", image_error)
                p.hw('INIT')
        p.textln("")
        p.textln("")

        p.set(align='left', bold=False)
        if card.get('type_line'):
            p.textln(format_type_line(front_face_text(card['type_line'])))
            p.textln("")

        oracle_text = card.get('oracle_text')
        if oracle_text:
            p.set(align='left', font='a')
            print_wrapped_text(oracle_text)

        if card.get('power') and card.get('toughness'):
            p.set(align='right', bold=True, custom_size=True, width=2, height=2)
            p.textln(f"{card['power']}/{card['toughness']}")

        p.set(align='left', bold=False, normal_textsize=True)
        p.textln("")
        p.textln("")
        p.textln("")
    except Exception as e:
        print("An error occurred:", e)

def print_vanguard():
    p.hw('INIT')
    print_image_paced(os.path.join(BASE_DIR, "avatar.bmp"))



try:
    while True:
        # Read the state of the switch/button
        up_button_state = not IO.input(UP_BUTTON_PIN)
        down_button_state = not IO.input(DOWN_BUTTON_PIN)
        print_button_state = not IO.input(PRINT_BUTTON_PIN)
        vanguard_button_state = not IO.input(VANGUARD_BUTTON_PIN)

        if(up_button_state):
            count += 1
            count = count % 17
            time.sleep(0.2)

        if(down_button_state):
            count += 16
            count = count % 17
            time.sleep(0.2)

        if(vanguard_button_state):
            PORT(0x73)
            print_vanguard()

        if(print_button_state and count != 14):
            PORT(0x73)
            print_random_card(count)
            

        pin = DISPLAY[count]        # assigning value to 'pin' for each digit
        PORT(pin);                  # showing each digit on display 


except KeyboardInterrupt:
    print("\nExiting...")
    # Clean up IO settings
    IO.cleanup()
