#!/bin/bash

# get USER, HOME and DISPLAY and then completely clear environment
U=$USER
H=$HOME
D=$DISPLAY

for i in $(env | awk -F"=" '{print $1}') ; do
unset $i ; done

