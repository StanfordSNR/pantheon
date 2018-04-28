#!/bin/sh -x

# update mahimahi source line and package listings
sudo add-apt-repository -y ppa:keithw/mahimahi
sudo apt-get update

# install required packages
sudo apt-get -y install mahimahi ntp ntpdate texlive python-pip
pip install --user matplotlib numpy tabulate pyyaml

# install pantheon tunnel
sudo apt-get -y install debhelper autotools-dev dh-autoreconf iptables \
                        pkg-config iproute2

DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
cd $DIR/third_party/pantheon-tunnel && ./autogen.sh && ./configure && \
make -j2 && sudo make install
