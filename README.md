# mb_thermal_printer
<a href='https://ko-fi.com/oboyone' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' />


Here are the scripts and steps i took to create a momir basic thermal printer, using a cheap thermal printer and a  raspberry pi

A step by step on how this was done is 

- Get the latest MTGJSON AtomicCards.json file from mtgjson.com
- Extract the scryfall id's and other useful information form the JSON file
- Get card data (name, cost, type, text, power/toughness, art url) from Scryfall and save it to `cards.json`
- Download only the card art (not the full card image) from Scryfall, one folder per cmc
- Using imagemagick convert the art jpgs to monochrome grayscale
- Connect buttons, thermal printer and OLED screen to Raspberry Pi GPIO pins
- Add python script, cards.json, and art files to Raspberry Pi
- Add python script to crontab startup so that it is automatically started when the Pi is powered on

Description of files: <br />
**get_card_data_from_scryfall.py** - Get card data (name, mana cost, type, oracle text, power/toughness, art URL) from Scryfall's API and merge it into `cards.json` <br />
**cleanup_cards.py** - Removes records whose front face is not a creature from `cards.json` (land creatures are allowed); run without options for a dry run, or with `--write` to save the cleanup <br />
**download_art_from_scryfall.py** - Downloads only the card art (via Scryfall's `art_crop`) into folders keyed by cmc and scryfall id <br />
**convert_images_to_monochrome.sh** - Converts the art JPG files into monochrome BMP files, this needs to be run on a Linux installation with imagemagick <br />
**momir.py** - Actual python program that runs on the Pi for the printer. Prints the card's name/type/text/power-toughness using the printer's text methods, and the art as a bitmap image <br />
**restart.py** - Watches a button and restarts the momir service <br />
**run_momir.sh / run_restart.sh** - Wrappers used by systemd/crontab to launch the scripts with the venv python <br />
**avatar.py, test.py** - Small printer test scripts <br />
**button.py, 5press.py, count.py, display.py, step-res.py** - GPIO test scripts for the buttons and the 7 segment display <br />
**requirements.txt** - Local/dev Python dependencies (`pip install -r requirements.txt`) <br />
**requirements-pi.txt** - Raspberry Pi runtime dependencies, including GPIO support <br />
**Makefile** - `make install` creates the venv in the project root and installs Raspberry Pi runtime dependencies. On macOS, use `make install-mac`. On the Pi, use `make install VENV_FLAGS=--system-site-packages` if you installed RPi.GPIO with apt <br />
**cards.json** - Card database (name, mana cost, type line, oracle text, power/toughness, art URL) keyed by scryfall id. Git ignores this file <br />
**art/** - Downloaded card art, one folder per cmc, with the printable BMPs in `art/<cmc>/converted_files/`. Git ignores this folder <br />

I used the following hardware <br />
3x KY-004 Push Button  <br />
3x 1k OHM Resistors (optional, but will extend the lifetime of your buttons. They should be placed between the 3.3v and the button in that case) <br />
1x 3 x 0.91" OLED 128 x 32 pixels I2C Screen <br />
1x Raspberry Pi 4 <br />
1x QR204 Thermal Printer <br />
1x 12V Female 2.1mm x 5.5mm DC Power Jack Adapter <br />
1x 9v 2A Male DC Power Adapter <br />
1x Power cable for Raspberry PI <br />
1x Soldering Breadboard <br />
1x 32gb micro SD card <br />
Dupont Cables <br  />

I started the project with the aim of using a Arduino UNO instead of the Raspberry PI, but after many hours of troubleshooting and retrying things I realized that my thermal printer simply was incompatible with most common thermal printer modules for the Arduino. <br /> <br /> I could never get it to print images no matter what I tried. So I ended up pivoting to the Rapsberry Pi instead. I am sure that you can get this to work on a Arduino with a compatible thermal printer, if so you probably want to use imagemagick to convert the monochrome images to BIN files instead, the code for that would look something like this


# Convert to BIN example

#Create a new folder for the binary files

mkdir -p ../binary_files

#Iterate through each BMP file and convert it to binary (PBM), remove header, and pad zero

for file in *.bmp; do
    echo "Creating BIN file for: $file" 

    # Define the output filename in the binary_files directory by replacing the extension with pbm
    output_file="../binary_files/$(basename -- "$file" .bmp).pbm"

    # Use ImageMagick's convert command to convert BMP to binary (PBM) with a depth of 1
    convert "$file" -threshold 50% -compress none pbm:- | \
    
    # Remove the PBM header and pad zeros to make the height even
    awk 'NR>2 {print $0} END{if(NR%2!=0) print "0"}' > "$output_file"
done
