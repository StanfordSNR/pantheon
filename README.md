[![Build Status](https://travis-ci.org/StanfordSNR/pantheon.svg?branch=master)](https://travis-ci.org/StanfordSNR/pantheon)

# Disclaimer:
This is unfinished research software.
Multiple scripts run commands as root to install prerequisite programs, update package lists, etc.
Our scripts will write to the filesystem in the pantheon folder and in /tmp/.
We have not implemented most of the programs run by our wrappers.
Those programs may write to the filesystem (for example, Verus will write files like `client_45191.out`  and a folder named `verus_tmp` into the current working directory when it is called).
We never run third party programs as root, but we can not guarantee they will never try to escalate privilege to root.

Run at your own risk. Feel free to contact our mailing list: `the name of this repository`@cs.stanford.edu

# Pantheon of Congestion Control
The Pantheon has wrappers for many popular and research congestion control schemes.
It allows them to run over a common interface and has tools to benchmark and compare their performance.
Pantheon tests can be run locally over an emulated link using [mahimahi](http://mahimahi.mit.edu/) or over the internet to a remote machine.

## Preparation
Many of the tools and programs run by the Pantheon are git submodules in the `third_party` folder.
To clone this repository, including submodules, run:

```
git clone --recursive https://github.com/StanfordSNR/pantheon.git
```

To add submodules after cloning, run:
```
git submodule update --init
```


## Running the Pantheon
Currently supported schemes can be found in `src/`. Running:

```
test/run.py
```

Will setup and run all congestion control schemes in the Pantheon locally (and remotely if the `-r` flag is used).
Multiple flows can be run simultaneously with `-f`.
The running time of each scheme can be specified with `-t` and the entire experiment can be run multiple times using `--run-times`.
Logs of all packets sent and received will be written to `test/` for later analysis.


Run `test/run.py -h` for detailed usage and additional optional arguments.


To run over an arbitrary set of mahimahi shells locally run:
```
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

test/run.py --run-only setup
mm-delay 50 mm-loss uplink .1 mm-loss downlink .1 mm-link /usr/share/mahimahi/traces/TMobile-LTE-short.up /usr/share/mahimahi/traces/TMobile-LTE-short.down -- sh -c 'test/run.py -r $USER@$MAHIMAHI_BASE:pantheon --run-only test'  # assumes pantheon in home directory
```

## Pantheon analysis
Before performing analysis run:
```
analysis/analysis_pre_setup.py
```

To analyze experiment logs in the `test/` directory run:
```
analyze/analyze.py --data-dir test/
```
This will generate charts and `pantheon_report.pdf `in the `data-dir` folder


To compare two Pantheon experiments, one can use `analyze/compare_two_experiments.py` with directories, xz archives, or archive URLs from Pantheon experiments.


## Running a single congestion control scheme
Before performing experiments individually run:
```
test/pre_setup.py
```

To make and install the `sprout` and it's dependencies run:

```
test/setup.py sprout
```

Run `test/setup.py -h` for detailed usage and additional optional arguments.

To test `sprout` over an emulated link run:
```
test/test.py [-t RUNTIME] [-f FLOWS] congestion-control
```

To setup and test `sprout` over the wide area to a remote machine run:
```
test/pre_setup.py -r REMOTE:PANTHEON-DIR
test/setup.py -r REMOTE:PANTHEON-DIR sprout
test/test.py -r REMOTE:PANTHEON-DIR [-t RUNTIME] [-f FLOWS] sprout
```

Run `test/test.py -h` for detailed usage and additional optional arguments.

## Running schemes without any logging
Run `test/pre_setup.py` and `test/setup.py <congestion-control>` first.

Find running order for scheme:
```
./<congestion-control>.py who_goes_first
```

Depending on the output of `who_goes_first`, run

```
# Receiver first
./<congestion-control>.py receiver
./<congestion-control>.py sender IP port
```

or

```
# Sender first
./<congestion-control>.py sender
./<congestion-control>.py receiver IP port
```
