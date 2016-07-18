#!/bin/sh -xe

# Install mahimahi and inkscape
sudo add-apt-repository -y ppa:keithw/mahimahi
sudo add-apt-repository -y ppa:inkscape.dev/stable
sudo apt-get -yq update
sudo apt-get -yq --force-yes install mahimahi inkscape

# Add NodeSource PPA (to access the latest nodejs)
curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -

# Install TeX Live
sudo apt-get install -yq --force-yes texlive
