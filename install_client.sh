#!/usr/bin/env bash



## This script is intended for a raspberry pi with a freshly installed raspbian
##It will install all the necessities to run the client

sudo apt-get purge wolfram-engine
sudo apt-get upgrade
sudo apt-get dist-upgrade

sudo apt-get isntall batmand
sudo apt-get install batctl


sudo pip3 install pymavlink
sudo pip3 install dronekit

sudo pip3 install Adafruit-SSD1306

sudo apt-get install -y i2c-tools
sudo apt-get install python-imaging python-smbus
sudo apt-get install nmap
