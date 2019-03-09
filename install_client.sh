#!/usr/bin/env bash



## This script is intended for a raspberry pi with a freshly installed raspbian
##It will install all the necessities to run the client
NEWHOSTNAME=$1

sudo sed -i "1s/.*/$NEWHOSTNAME" /etc/hostname
sudo apt-get purge wolfram-engine
sudo apt-get upgrade
sudo apt-get dist-upgrade
sudo setxkbmap us
sudo apt-get install python-dev
sudo apt-get install libxml2
sudo apt-get install libxml2-dev libxslt-dev
sudo apt-get install libzbar-dev libzbar0
sudo apt-get install python3-lxml
sudo pip3 install lxml
sudo apt-get isntall batmand
sudo apt-get install batctl



sudo pip3 install dronekit
sudo pip3 uninstall pymavlink
sudo pip3 install pymavlink

sudo pip3 install Adafruit-SSD1306

sudo apt-get install -y i2c-tools
sudo apt-get install python-imaging python-smbus
sudo apt-get install nmap

