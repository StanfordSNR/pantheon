#!/bin/sh -xe

# mahimahi
sudo add-apt-repository -y ppa:keithw/mahimahi
sudo apt-get -yq update
sudo apt-get -yq --force-yes install mahimahi
curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
