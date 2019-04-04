#!/bin/bash
sudo modprobe batman-adv
# Credit to EveningStarNM: https://www.reddit.com/r/darknetplan/comments/68s6jp/how_to_configure_batmanadv_on_the_raspberry_pi_3/
# disable wlan0

sudo ifconfig wlan1 down &
sudo ifconfig wlan1 mtu 1532 &
sleep 1s
sudo iwconfig wlan1 mode ad-hoc &
sudo iwconfig wlan1 essid making-a-mesh-of-it ap 02:12:34:56:78:9A &
sudo iwconfig wlan1 channel 8 &
sleep 1s
sudo batctl if add wlan1 &
sleep 1s
sudo ifconfig bat0 up &
sleep 5s
sudo ifconfig wlan1 up