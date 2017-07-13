#!/bin/bash
# Program name: pingall.sh
date
cat temp.txt |  while read output
do
    ping -W 1 -c 1 "$output" > /dev/null 
    if [ $? -eq 0 ]; then
    echo "node $output is up" 
    else
    echo "node $output is down"
    fi
done
