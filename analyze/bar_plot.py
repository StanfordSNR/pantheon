#!/usr/bin/env python

import sys
import numpy as np
import matplotlib.pyplot as plt

schemes = []
tput_list = []
delay_list = []

max_tput = 0
min_tput = sys.maxint

max_delay = 0
min_delay = sys.maxint

with open('variation') as f:
    while True:
        cc = f.readline()
        if not cc:
            break
        else:
            cc = cc.strip()

        schemes.append(cc)
        tput_cc = map(float, f.readline().split())
        max_tput = max(max_tput, max(tput_cc))
        min_tput = min(min_tput, min(tput_cc))
        tput_list.append(tput_cc)

        delay_cc = map(float, f.readline().split())
        max_delay = max(max_delay, max(delay_cc))
        min_delay = min(min_delay, min(delay_cc))
        delay_list.append(delay_cc)


schemes = ['Cubic', 'Vegas', 'LEDBAT', 'PCC', 'Verus', 'SCReAM', 'Sprout', 'WebRTC', 'QUIC']

fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()

ax1.boxplot(tput_list, showfliers=False)
print min_tput, max_tput
ax1.set_xticklabels(schemes, fontsize=12)
ax1.set_ylim(ymin=-0.05, ymax=1.05)
ax1.set_ylabel('Relative throughput', fontsize=14)

ax2.boxplot(delay_list, showfliers=False)
print min_delay, max_delay
ax2.set_xticklabels(schemes, fontsize=12)
ax2.set_ylim(ymin=0.5, ymax=10.5)
ax2.set_ylabel('Relative delay', fontsize=14)

fig1.savefig('throughput-boxplot.svg', format='svg')
fig2.savefig('delay-boxplot.svg', format='svg')
