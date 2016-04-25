#!/bin/sh

sudo add-apt-repository -y ppa:keithw/mahimahi
sudo apt-get update
sudo apt-get -y --force-yes install mahimahi
sudo sysctl -w net.ipv4.ip_forward=1

sudo apt-get -y --force-yes install build-essential autoconf libtbb-dev \
libasio-dev libalglib-dev libboost-system-dev python-pip iperf libnss3-tools
pip install interruptingcow
