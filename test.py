from escpos.printer import Serial
import os, random, sys

IMAGE_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

p = Serial(devfile='/dev/serial0', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1.00, dsrdtr=True) #initilize thermal printer serial 


def print_random_image(cmc): #function to print image
    path = os.path.join(IMAGE_ROOT, str(cmc), 'converted_files')
    try:
        image_path = os.path.join(path, random.choice(os.listdir(path)))
        p.image(image_path)
        p.textln("")
        p.textln("")
        p.textln("")
    except Exception as e:
        print("An error occurred:", e)

cmc = 0
if sys.argv[1]:
    cmc = sys.argv[1]

print_random_image(cmc)


