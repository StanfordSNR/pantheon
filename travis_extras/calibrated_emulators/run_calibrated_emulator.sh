#! /bin/bash -xe

BANDWIDTH=$1
DELAY=$2
QUEUE=$3
UP_LOSS=$4
DOWN_LOSS=$5
DIR=$6
SCHEMES=$7

test/run.py --uplink-trace ../$DIR"$BANDWIDTH"mbps.trace --downlink-trace ../$DIR"$BANDWIDTH"mbps.trace --prepend-mm-cmds "mm-delay $DELAY mm-loss uplink $UP_LOSS mm-loss downlink $DOWN_LOSS" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=$QUEUE" --schemes "$SCHEMES" --run-times 2

analyze/analysis_pre_setup.py
analyze/compare_two_experiments.py $DIR test/ --analyze-schemes "$SCHEMES"
