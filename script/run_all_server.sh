#!/bin/bash

cat hostname.txt | while read ip var2 ; do
    ssh -t $ip "rm *.tmp" &
    echo "$var2"
    #scp -r ~/microservices/application/robot-shop $ip:~
    
    #ssh $ip "cd ~/robot-shop; echo cloud123 | sudo -S bash create_all.sh" &
    #ssh $ip "echo cloud123 | sudo -S docker image ls | grep kevin2333" &
    sleep 3
done

