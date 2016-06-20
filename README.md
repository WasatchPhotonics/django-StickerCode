# StickerCode
[![Build Status](https://travis-ci.org/WasatchPhotonics/StickerCode.svg?branch=master)](https://travis-ci.org/WasatchPhotonics/StickerCode) [![Coverage Status](https://coveralls.io/repos/WasatchPhotonics/StickerCode/badge.svg?branch=master&service=github)](https://coveralls.io/github/WasatchPhotonics/StickerCode?branch=master)

Web service to create qr codes, short links and QL-700 shaped stickers
for device serialization.


![StickerCode screenshot](/resources/demo.gif "StickerCode screenshot")

Getting Started
---------------

PyQRNative is required. Use the fork here:
https://github.com/WasatchPhotonics/pyqrnative for a typo correction on
linux.

Full installation prerequisites for Fedora Core 22:

    Create a python virtual environment
    sudo dnf install freetype-devel
    sudo dnf install gcc
    sudo dnf install libjpeg-devel
    sudo dnf install zlib-devel
    sudo dnf install ImageMagick-devel

    git clone https://github.com/WasatchPhotonics/pyqrnative
    cd pyqrnative
    $VENV/bin/python setup.py install


Conda Installation and tests
----------------------------
    conda create -n cookbook pyramid
    source activate cookbook
    conda install pillow pytest-cov

    git clone https://github.com/WasatchPhotonics/pyqrnative
    cd pyqrnative
    $VENV/bin/python setup.py install


Setup and Tests
---------------

- cd _directory containing this file_

- $VENV/bin/python setup.py develop

- $VENV/bin/nosetests --cover-erase --with-coverage --cover-package=stickercode

- $VENV/bin/pserve config/development.ini

