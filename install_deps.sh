#!/bin/sh -xe

sudo add-apt-repository -y ppa:keithw/mahimahi
sudo apt-get update
sudo apt-get -y --force-yes install mahimahi
sudo sysctl -w net.ipv4.ip_forward=1

sudo apt-get -y --force-yes install python-pip iperf libnss3-tools
pip install interruptingcow
