#!/bin/bash
#kill everything
#sudo update-rc.d ifplugd disable
#sudo update-rc.d dhcpcd disable 
#sudo sed -i 's/disabled\=1/disabled\=0/g' ~/../../etc/wpa_supplicant/wpa_supplicant.conf


echo "starting wifi setup"
USERNAME=$1
PASSWORD=$2
IP_ADDRESS=$3
sudo killall wpa_supplicant
./wifisetup.sh $USERNAME $PASSWORD
sudo wpa_supplicant -c /etc/wpa_supplicant/wpa_supplicant.conf -i wlan0 &
sudo ifconfig wlan0 up &
sleep 20s
./wifidefault.sh

sudo systemctl stop dhcpd.service
#give batman a little probe

sudo modprobe batman-adv

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
sudo ifconfig bat0 $IP_ADDRESS &
sudo ifconfig wlan1 up
