#!/bin/bash
sudo rm /etc/network/interfaces
sudo rm /etc/wpa_supplicant/wpa_supplicant.conf

touch  /etc/network/interfaces
touch  /etc/wpa_supplicant/wpa_supplicant.conf
#wpa succ
echo 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev' >> /etc/wpa_supplicant/wpa_supplicant.conf
echo 'update_config=1' >> /etc/wpa_supplicant/wpa_supplicant.conf
echo 'country=US' >> /etc/wpa_supplicant/wpa_supplicant.conf 
echo '' >> /etc/wpa_supplicant/wpa_supplicant.conf
echo 'network={
     ssid="UNT"
     proto=RSN
     key_mgmt=WPA-EAP
     group=CCMP TKIP
     identity="mtw0050" 
     password=$HASHWORD
     phase1="peaplabel=0"
     phase2="auth=MSCHAPV2"
     }' >> /etc/wpa_supplicant/wpa_supplicant.conf

#interfaces crap



echo 'source-directory /etc/network/interfaces.d' >> /etc/network/interfaces
echo 'auto lo' >> /etc/network/interfaces
echo 'iface lo inet loopback' >> /etc/network/interfaces



echo 'allow-hotplug wlan0' >> /etc/network/interfaces
echo 'iface wlan1 inet manual' >> /etc/network/interfaces
echo 'wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf' >> /etc/network/interfaces
