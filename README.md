# On/Off Monitor Device
## Installation
### Cryptography
On Linux you might need to install Rust to compile the Cryptography library. See their [installation instructions](https://cryptography.io/en/latest/installation/)  
For installing Rust on Raspberry Pi see https://forums.raspberrypi.com/viewtopic.php?t=289963
## For when testing on a non-Raspberry Pi
Instead of installing the `RPi.GPIO` module, you can install `rpi-gpio-emu`.
Installing with pipenv won't work as `RPi.GPIO` only works with Raspberry Pi.
