#!/bin/bash
sudo rm /etc/network/interfaces
sudo rm /etc/wpa_supplicant/wpa_supplicant.conf

touch rm /etc/network/interfaces
touch rm /etc/wpa_supplicant/wpa_supplicant.conf

#wpa succ
echo 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev' >> /etc/wpa_supplicant/wpa_supplicant.conf
echo 'update_config=1' >> /etc/wpa_supplicant/wpa_supplicant.conf
echo 'country=US' >> /etc/wpa_supplicant/wpa_supplicant.conf

#interfaced

echo 'source-directory /etc/network/interfaces.d' >> /etc/network/interfaces
echo 'auto lo' >> /etc/network/interfaces
echo 'iface lo inet loopback' >> /etc/network/interfaces
