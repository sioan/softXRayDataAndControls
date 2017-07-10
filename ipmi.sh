#!/bin/bash
ipmitool -I lanplus -U ADMIN -P ipmia8min -H $1 power $2
