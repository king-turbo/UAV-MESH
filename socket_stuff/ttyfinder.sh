#!/bin/bash

rm "sysdisc.txt"
for VARIABLE in 0 1 2 3 4 5
do

    if udevadm info --query=all --name=/dev/ttyACM$VARIABLE | grep --q "Arduino_Mega"; then
    touch "sysdisc.txt"
    echo "/dev/ttyACM""$VARIABLE" >> "sysdisc.txt"
    echo "ardupilot" >> "sysdisc.txt"
    fi
done

    
    
    
