[![Build Status](https://travis-ci.org/StanfordLPNG/pantheon.svg?branch=master)]
(https://travis-ci.org/StanfordLPNG/pantheon)

# Pantheon of Congestion Control
Pantheon tests can be run locally over emulated mahimahi link or between local
and remote machines over real networks.

## Preparation
On local machine (and remote machine), clone the repository and get submodules:

```
git clone https://github.com/StanfordLPNG/pantheon.git
git submodule update --init
```

Install dependencies to generate summary plots and reports of experiments:

```
sudo apt-get install texlive python-matplotlib ntp
```

## Setup
First, change directory to `test` and run:

```
./pre_setup.py
```

Then

```
./setup.py congestion-control
```

Currently the supported `congestion-control` is `default_tcp`, `vegas`,
`ledbat`, `pcc`, `scream`, `sprout`, `verus`, `koho_cc`, `webrtc` and `quic`.

Alternatively, set up on both local and remote machines:

```
./pre_setup.py -r REMOTE:PANTHEON-DIR
./setup.py -r REMOTE:PANTHEON-DIR congestion-control
```

Run `./setup.py -h` for detailed usage.

## Test
Test congestion control schemes on local machine:

```
./test.py [-t RUNTIME] [-f FLOWS] congestion-control
```

or between local machine and remote machine:

```
./test.py -r REMOTE:PANTHEON-DIR [-t RUNTIME] [-f FLOWS] congestion-control
```

`-f 0` indicates that no tunnels would be created in the tests; otherwise,
there will be `FLOWS` tunnels created to run a congestion control scheme.
Notice that if `-r` is given, `FLOWS` must be positive.

Alternatively, run

```
./run.py [-r REMOTE:PANTHEON-DIR] [-t RUNTIME] [-f FLOWS]
```

to set up and test all congestion control schemes. In addition, a summary
report `pantheon_report.pdf` of the experiments will be generated.

Run `./test.py -h` and `./run.py -h` for detailed usage, including more
optional arguments.

## Usage of Individual Scheme
Change directory to `src` first.

```
# print the dependencies required to be installed
./<congestion-control>.py deps

# perform build commands for scheme
./<congestion-control>.py build

# run initialize commands after building and before running
./<congestion-control>.py init

# find running order for scheme
./<congestion-control>.py who_goes_first

# find friendly name of scheme
./<congestion-control>.py friendly_name
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
