#!/bin/sh
cd external

# build sourdough
cd sourdough
./autogen.sh
./configure
make
cd ..

# build libutp
cd libutp 
make
cd ..

# build proto-quic
# cd proto-quic
# export PATH=$PATH:`pwd`/depot_tools
# ./src/build/install-build-deps.sh
# cd src
# gclient runhooks && ninja -C out/Release quic_client quic_server net_unittests
