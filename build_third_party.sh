#!/bin/sh

proj_dir=$( cd $(dirname $0) ; pwd )
third_party_dir=$proj_dir/third_party

# build libutp
cd $third_party_dir/libutp
make

# build proto-quic
cd $third_party_dir/proto-quic
export PATH=$PATH:`pwd`/depot_tools
./src/build/install-build-deps.sh --no-prompt

cd $third_party_dir/proto-quic/src
gclient runhooks && ninja -C out/Release quic_client quic_server net_unittests
