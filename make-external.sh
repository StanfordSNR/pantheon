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
