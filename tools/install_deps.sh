#!/bin/sh -x

# update mahimahi source line and package listings when necessary
sudo add-apt-repository -y ppa:keithw/mahimahi
sudo apt-get update

# install required packages
sudo apt-get -y install mahimahi ntp ntpdate texlive python-pip
sudo pip install matplotlib numpy tabulate pyyaml

# install pantheon tunnel
sudo apt-get -y install debhelper autotools-dev dh-autoreconf iptables \
                        pkg-config iproute2

CURRDIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
cd $CURRDIR/../third_party/pantheon-tunnel && ./autogen.sh && ./configure \
&& make -j && sudo make install
