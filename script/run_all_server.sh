#!/bin/bash

cat hostname.txt | while read ip var2 ; do
    ssh -t $ip "rm Jun*" &
    sleep 5
done

