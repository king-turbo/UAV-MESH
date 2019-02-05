
for VARIABLE in 0 1 2 3 4 5
do

    if udevadm info --query=all --name=/dev/ttyACM$VARIABLE | grep --q "Arduino_Mega"; then
    echo "/dev/ttyACM""$VARIABLE"
    fi
done

    
    
    
