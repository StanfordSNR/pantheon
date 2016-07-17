#!/bin/sh -xe

proj_dir=$( cd $(dirname $0) ; pwd )
test_dir=$proj_dir/test

cd $test_dir
./test.py default_tcp
./test.py vegas
./test.py ledbat
./test.py pcc
./test.py verus
./test.py scream
./test.py webrtc
./test.py sprout
# Put the most time-consuming QUIC at the end
./test.py quic
