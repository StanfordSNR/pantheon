#!/bin/sh

data_dir="indigo-$1-checkpoint-$2"

./test.py local --schemes indigo --data-dir "$data_dir/nepal-wireless-1flow" --pkill-cleanup --uplink-trace 0.57mbps-poisson.trace --downlink-trace 0.57mbps-poisson.trace --prepend-mm-cmds "mm-delay 28 mm-loss uplink 0.0477" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=14"
../analysis/analyze.py --data-dir "$data_dir/nepal-wireless-1flow"

./test.py local --schemes indigo --data-dir "$data_dir/mexico-cellular-1flow" --pkill-cleanup --uplink-trace 2.64mbps-poisson.trace --downlink-trace 2.64mbps-poisson.trace --prepend-mm-cmds "mm-delay 88" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=130"
../analysis/analyze.py --data-dir "$data_dir/mexico-cellular-1flow"

./test.py local --schemes indigo --data-dir "$data_dir/colombia-cellular-1flow" --pkill-cleanup --uplink-trace 3.04mbps-poisson.trace --downlink-trace 3.04mbps-poisson.trace --prepend-mm-cmds "mm-delay 130" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=426"
../analysis/analyze.py --data-dir "$data_dir/colombia-cellular-1flow"

./test.py local --schemes indigo --data-dir "$data_dir/att-lte-driving-2016" --pkill-cleanup --uplink-trace ATT-LTE-driving-2016.up --downlink-trace ATT-LTE-driving-2016.down --prepend-mm-cmds "mm-delay 80"
../analysis/analyze.py --data-dir "$data_dir/att-lte-driving-2016"

./test.py local --schemes indigo --data-dir "$data_dir/att-lte-driving" --pkill-cleanup --uplink-trace ATT-LTE-driving.up --downlink-trace ATT-LTE-driving.down --prepend-mm-cmds "mm-delay 60"
../analysis/analyze.py --data-dir "$data_dir/att-lte-driving"

./test.py local --schemes indigo --data-dir "$data_dir/verizon-lte-driving" --pkill-cleanup --uplink-trace Verizon-LTE-driving.up --downlink-trace Verizon-LTE-driving.down --prepend-mm-cmds "mm-delay 40"
../analysis/analyze.py --data-dir "$data_dir/verizon-lte-driving"

./test.py local --schemes indigo --data-dir "$data_dir/verizon-evdo-driving" --pkill-cleanup --uplink-trace Verizon-EVDO-driving.up --downlink-trace Verizon-EVDO-driving.down --prepend-mm-cmds "mm-delay 50"
../analysis/analyze.py --data-dir "$data_dir/verizon-evdo-driving"

./test.py local --schemes indigo --data-dir "$data_dir/tmobile-umts-driving" --pkill-cleanup --uplink-trace TMobile-UMTS-driving.up --downlink-trace TMobile-UMTS-driving.down --prepend-mm-cmds "mm-delay 70"
../analysis/analyze.py --data-dir "$data_dir/tmobile-umts-driving"
