#!/bin/bash
#kill everything
#sudo update-rc.d ifplugd disable
#sudo update-rc.d dhcpcd disable 
#sudo sed -i 's/disabled\=1/disabled\=0/g' ~/../../etc/wpa_supplicant/wpa_supplicant.conf

echo "starting wifi setup"

sudo killall wpa_supplicant
./wifisetup.sh
sudo wpa_supplicant -c /etc/wpa_supplicant/wpa_supplicant.conf -i wlan1 &
sudo ifconfig wlan1 up &
sleep 20s
./wifidefault.sh

sudo systemctl stop dhcpd.service
#give batman a little probe

sudo modprobe batman-adv

# disable wlan0



echo "wsup again"
sudo ifconfig wlan0 down &
sleep 1s
sudo iwconfig wlan0 mode ad-hoc &
sudo iwconfig wlan0 essid making-a-mesh-of-it ap 02:12:34:56:78:91 &
sudo iwconfig wlan0 channel 8 &
sleep 1s
sudo batctl if add wlan0 &
sleep 1s
sudo ifconfig bat0 up &
sleep 5s
sudo ifconfig bat0 172.27.0.1/16 &
sudo ifconfig wlan0 up
