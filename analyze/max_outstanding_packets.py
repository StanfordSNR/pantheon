#!/usr/bin/env python

import sys
import math
import argparse
import numpy as np
import matplotlib_agg
import matplotlib.pyplot as plt



max_outstanding_packets = 0
outstanding_packets = dict()
with open(sys.argv[1]) as tunlog:
    for line in tunlog.readlines():
        if line.startswith('#'):
            continue

        words = line.split()
        timestamp = int(round(float(words[0])))
        if len(words) == 4:
            assert words[1] == '+'
            prop_delay = int(round(float(words[3])))
            for i in range(timestamp-prop_delay, timestamp):
                if i in outstanding_packets:
                    outstanding_packets[i] += 1
                else:
                    outstanding_packets[i] = 1
        elif len(words) == 5:
            assert words[1] == '-'
        else:
            assert False, line
    print max(outstanding_packets.itervalues())
