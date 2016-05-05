#!/bin/sh -xe

# Mahimahi
sudo add-apt-repository -y ppa:keithw/mahimahi
sudo apt-get -yq update
sudo apt-get -yq --force-yes install mahimahi
sudo sysctl -w net.ipv4.ip_forward=1

# Default TCP
sudo apt-get -yq --force-yes install iperf

# QUIC
# generate certificate using certutil
sudo apt-get -yq --force-yes install libnss3-tools
# build dependencies
dev_list="bison cdbs curl dpkg-dev elfutils devscripts fakeroot flex 
          git-core git-svn gperf libapache2-mod-php5 libasound2-dev 
          libbrlapi-dev libav-tools libbz2-dev libcairo2-dev libcap-dev 
          libcups2-dev libcurl4-gnutls-dev libdrm-dev libelf-dev 
          libffi-dev libgconf2-dev libglib2.0-dev
          libglu1-mesa-dev libgnome-keyring-dev libgtk2.0-dev libkrb5-dev
          libnspr4-dev libnss3-dev libpam0g-dev libpci-dev libpulse-dev
          libsctp-dev libspeechd-dev libsqlite3-dev libssl-dev libudev-dev
          libwww-perl libxslt1-dev libxss-dev libxt-dev libxtst-dev openbox
          patch perl php5-cgi pkg-config python-cherrypy3 python-crypto
          python-dev python-numpy python-opencv python-openssl python-psutil
          python-yaml rpm ruby subversion wdiff zip" 

lib_list="libatk1.0-0 libc6 libasound2 libcairo2 libcap2 libcups2 libexpat1
          libffi6 libfontconfig1 libfreetype6 libglib2.0-0 libgnome-keyring0
          libgtk2.0-0 libpam0g libpango1.0-0 libpci3 libpcre3 libpixman-1-0
          libpng12-0 libspeechd2 libstdc++6 libsqlite3-0 libx11-6 libxau6
          libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxdmcp6 libxext6
          libxfixes3 libxi6 libxinerama1 libxrandr2 libxrender1 libxtst6
          zlib1g"
sudo apt-get -yq --force-yes install $dev_list $lib_list
