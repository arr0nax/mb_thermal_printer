PYTHON ?= python3
# use `make install VENV_FLAGS=--system-site-packages` to reuse apt-installed RPi.GPIO
VENV_FLAGS ?=
PIP := ./bin/pip

.DEFAULT_GOAL := install

.PHONY: install install-mac seed venv clean

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-pi.txt

install-mac: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

seed:
	./bin/python get_card_data_from_scryfall.py
	./bin/python cleanup_cards.py --write
	./bin/python download_art_from_scryfall.py
	./convert_images_to_monochrome.sh

# the venv lives in the project root, so bin/python3 is the interpreter
venv:
	$(PYTHON) -m venv $(VENV_FLAGS) .

clean:
	rm -rf bin lib lib64 include __pycache__
