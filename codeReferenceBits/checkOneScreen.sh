#!/bin/bash
HOST=$1
echo "ssh'ing to " $HOST
ssh $HOST screen -list

#to run this, need below
#echo psana | xargs -I {} checkOneScreen.sh {}
