#!/bin/sh

data_dir="indigo-$1-checkpoint-$2"

./test.py local --schemes indigo --data-dir "$data_dir/india-wired-1flow" --pkill-cleanup --uplink-trace 100.42mbps.trace --downlink-trace 100.42mbps.trace --prepend-mm-cmds "mm-delay 27" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=173"
../analysis/analyze.py --data-dir "$data_dir/india-wired-1flow"

./test.py local -f 2 --interval 15 --schemes indigo --data-dir "$data_dir/india-wired-2flows" --pkill-cleanup --uplink-trace 100.42mbps.trace --downlink-trace 100.42mbps.trace --prepend-mm-cmds "mm-delay 27" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=173"
../analysis/analyze.py --data-dir "$data_dir/india-wired-2flows"

./test.py local -f 3 --interval 10 --schemes indigo --data-dir "$data_dir/india-wired-3flows" --pkill-cleanup --uplink-trace 100.42mbps.trace --downlink-trace 100.42mbps.trace --prepend-mm-cmds "mm-delay 27" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=173"
../analysis/analyze.py --data-dir "$data_dir/india-wired-3flows"

./test.py local --schemes indigo --data-dir "$data_dir/china-wired-1flow" --pkill-cleanup --uplink-trace 77.72mbps.trace --downlink-trace 77.72mbps.trace --prepend-mm-cmds "mm-delay 51 mm-loss uplink 0.0006" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=94"
../analysis/analyze.py --data-dir "$data_dir/china-wired-1flow"

./test.py local -f 2 --interval 15 --schemes indigo --data-dir "$data_dir/china-wired-2flows" --pkill-cleanup --uplink-trace 77.72mbps.trace --downlink-trace 77.72mbps.trace --prepend-mm-cmds "mm-delay 51 mm-loss uplink 0.0006" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=94"
../analysis/analyze.py --data-dir "$data_dir/china-wired-2flows"

./test.py local -f 3 --interval 10 --schemes indigo --data-dir "$data_dir/china-wired-3flows" --pkill-cleanup --uplink-trace 77.72mbps.trace --downlink-trace 77.72mbps.trace --prepend-mm-cmds "mm-delay 51 mm-loss uplink 0.0006" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=94"
../analysis/analyze.py --data-dir "$data_dir/china-wired-3flows"

./test.py local --schemes indigo --data-dir "$data_dir/mexico-wired-1-flow" --pkill-cleanup --uplink-trace 114.68mbps.trace --downlink-trace 114.68mbps.trace --prepend-mm-cmds "mm-delay 45" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=450"
../analysis/analyze.py --data-dir "$data_dir/mexico-wired-1flow"

./test.py local -f 2 --interval 15 --schemes indigo --data-dir "$data_dir/mexico-wired-2-flows" --pkill-cleanup --uplink-trace 114.68mbps.trace --downlink-trace 114.68mbps.trace --prepend-mm-cmds "mm-delay 45" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=450"
../analysis/analyze.py --data-dir "$data_dir/mexico-wired-2flows"

./test.py local -f 3 --interval 10 --schemes indigo --data-dir "$data_dir/mexico-wired-3-flows" --pkill-cleanup --uplink-trace 114.68mbps.trace --downlink-trace 114.68mbps.trace --prepend-mm-cmds "mm-delay 45" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=450"
../analysis/analyze.py --data-dir "$data_dir/mexico-wired-3flows"
