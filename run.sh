#!/bin/sh -xe

proj_dir=$( cd $(dirname $0) ; pwd )
test_dir=$proj_dir/test

cd $test_dir
./setup.py default_tcp
./test.py  default_tcp

./setup.py vegas
./test.py  vegas

./setup.py ledbat
./test.py  ledbat

./setup.py pcc
./test.py  pcc

./setup.py verus
./test.py  verus

./setup.py scream
./test.py  scream

./setup.py webrtc
./test.py  webrtc

./setup.py sprout
./test.py  sprout

# run quic last as it takes the longest by far
./setup.py quic
./test.py  quic

# Assemble a throughput-delay plot
./summary-plot.pl pantheon_summary.pdf default_tcp vegas ledbat pcc verus scream webrtc sprout quic

# Combile all HTML reports into one
./combine_reports.py                   default_tcp vegas ledbat pcc verus scream webrtc sprout quic
