#!/bin/sh -xe

sudo apt-get -yq --force-yes install debian-archive-keyring
sudo apt-key update
sudo add-apt-repository -y ppa:keithw/mahimahi
sudo apt-get -yq update
sudo apt-get -yq --force-yes install mahimahi
sudo sysctl -w net.ipv4.ip_forward=1
sudo apt-get -yq --force-yes install iperf
