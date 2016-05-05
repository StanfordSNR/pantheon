#!/bin/sh -xe

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
