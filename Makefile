PYTHON ?= python3
# use `make install VENV_FLAGS=--system-site-packages` to reuse apt-installed RPi.GPIO
VENV_FLAGS ?=
PIP := ./bin/pip

.DEFAULT_GOAL := install

.PHONY: install install-mac update venv clean

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-pi.txt

install-mac: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

update:
	./bin/python update_cards.py

# the venv lives in the project root, so bin/python3 is the interpreter
venv:
	$(PYTHON) -m venv $(VENV_FLAGS) .

clean:
	rm -rf bin lib lib64 include __pycache__
