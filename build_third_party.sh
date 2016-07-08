#!/bin/sh -xe

sudo sysctl -w net.ipv4.ip_forward=1

proj_dir=$( cd $(dirname ${BASH_SOURCE[0]}) ; pwd )
third_party_dir=$proj_dir/third_party

# build libutp
cd $third_party_dir/libutp
make -j

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

# build verus
cd $third_party_dir/verus
autoreconf -i
./configure
make -j

# build scream
cd $third_party_dir/scream
git submodule update --init
./autogen.sh
./configure
make -j

# build webrtc
cd $third_party_dir/webrtc
npm install
wget -O /tmp/video.y4m http://media.xiph.org/video/derf/y4m/city_cif_15fps.y4m
node $third_party_dir/webrtc/app.js >/dev/null 2>&1 &
Xvfb :1 >/dev/null 2>&1 &
export DISPLAY=:1

# build sprout
cd $third_party_dir/sprout
./autogen.sh
./configure --enable-examples
make -j
export SPROUT_MODEL_IN=$third_party_dir/sprout/src/examples/sprout.model

# cd back to project's root directory
cd $proj_dir
