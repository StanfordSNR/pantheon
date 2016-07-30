#!/bin/sh -xe

proj_dir=$( cd $(dirname $0) ; pwd )
test_dir=$proj_dir/test

cd $test_dir
./setup.py default_tcp
./test_locally.py  default_tcp

./setup.py vegas
./test_locally.py  vegas

./setup.py ledbat
./test_locally.py  ledbat

./setup.py pcc
./test_locally.py  pcc

./setup.py verus
./test_locally.py  verus

./setup.py scream
./test_locally.py  scream

./setup.py webrtc
./test_locally.py  webrtc

./setup.py sprout
./test_locally.py  sprout

# run quic last as it takes the longest by far
./setup.py quic
./test_locally.py  quic

# Assemble a throughput-delay plot
./summary-plot.pl pantheon_summary.pdf default_tcp vegas ledbat pcc verus scream webrtc sprout quic

# Combile all HTML reports into one
./combine_reports.py                   default_tcp vegas ledbat pcc verus scream webrtc sprout quic
