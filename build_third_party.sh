#!/bin/sh -xe

sudo sysctl -w net.ipv4.ip_forward=1

proj_dir=$( cd $(dirname $0) ; pwd )
third_party_dir=$proj_dir/third_party

# build libutp
cd $third_party_dir/libutp
make

# build pcc
cd $third_party_dir/pcc/sender
make
cd $third_party_dir/pcc/receiver
make

# build proto-quic
cd $third_party_dir/proto-quic
export PATH=$PATH:`pwd`/depot_tools
cd $third_party_dir/proto-quic/src
gclient runhooks && ninja -C out/Release quic_client quic_server 
## initialize certificate using certutil
sudo apt-get -yq --force-yes install libnss3-tools
date +%s | sha256sum | base64 | head -c 32 > cert_pwd
mkdir -p $HOME/.pki/nssdb
certutil -d $HOME/.pki/nssdb -N -f cert_pwd
