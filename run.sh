#!/bin/sh -xe

proj_dir=$( cd $(dirname $0) ; pwd )
test_dir=$proj_dir/test

cd $test_dir
./setup.py default_tcp
./test_local.py  default_tcp

./setup.py vegas
./test_local.py  vegas

./setup.py ledbat
./test_local.py  ledbat

./setup.py pcc
./test_local.py  pcc

./setup.py verus
./test_local.py  verus

./setup.py scream
./test_local.py  scream

./setup.py webrtc
./test_local.py  webrtc

./setup.py sprout
./test_local.py  sprout

# run quic last as it takes the longest by far
./setup.py quic
./test_local.py  quic

# Assemble a throughput-delay plot
./summary-plot.pl pantheon_summary.pdf default_tcp vegas ledbat pcc verus scream webrtc sprout quic

# Combile all HTML reports into one
./combine_reports.py                   default_tcp vegas ledbat pcc verus scream webrtc sprout quic
