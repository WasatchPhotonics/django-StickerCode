# StickerCode
[![Build Status](https://travis-ci.org/WasatchPhotonics/StickerCode.svg?branch=master)](https://travis-ci.org/WasatchPhotonics/StickerCode) [![Coverage Status](https://coveralls.io/repos/WasatchPhotonics/StickerCode/badge.svg?branch=master&service=github)](https://coveralls.io/github/WasatchPhotonics/StickerCode?branch=master)

Django application to create qr codes, short links and QL-700 shaped stickers
for device serialization.


![StickerCode screenshot](/resources/demo.gif "StickerCode screenshot")

Getting Started
---------------

PyQRNative is required. Use the fork here:
https://github.com/WasatchPhotonics/pyqrnative for a typo correction on
linux.


System requirements on Linux 
----------------------------

    # Tested with Fedora Core 24
    dnf install freetype-devel gcc libjpeg-devel zlib-devel ImageMagick-devel

Conda environment creation
--------------------------

    # Tested with conda3 64 bit
    conda create --name django-StickerCode

    source activate django-StickerCode

    git clone https://github.com/WasatchPhotonics/pyqrnative
    cd pyqrnative
    python setup.py install

    conda install pillow pytest-cov

Setup and Tests
---------------

- cd _directory containing this file_

- python setup.py develop

- default django test command goes here

