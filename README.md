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

Then get texlive for report generation:

```
sudo apt-get install texlive
```

## Setup
Currently the supported `congestion-control` is `default_tcp`, `vegas`,
`ledbat`, `pcc`, `scream`, `sprout`, `verus`, `koho_cc`, `webrtc` and `quic`.

```
./test/setup.py congestion-control
```

or set up on both local and remote machines in one command:

```
./test/setup.py [-i IDENTITY-FILE] -r REMOTE:DIR congestion-control
```

Run `./test/setup.py -h` for detailed usage.

## Test
On local machine:

```
./test/test.py [-f FLOWS] [-t RUNTIME] [--interval INTERVAL] congestion-control
```

or between local machine and remote machine:

```
./test/test.py [-i IDENTITY-FILE] -r REMOTE:DIR [-f FLOWS] [-t RUNTIME]
               [--interval INTERVAL] congestion-control
```

`FLOWS=0` indicates that no tunnels would be created in the tests; otherwise,
there will be `FLOWS` tunnels created to run a congestion control scheme.
Notice that if `-r` is given, `FLOWS` must be positive.

Alternatively, run

```
./test/run.py [-i IDENTITY-FILE] [-r REMOTE:DIR] [-f FLOWS] [-t RUNTIME]
              [--interval INTERVAL]
```

to set up and test all congestion control schemes. In addition, a summary
report `test/pantheon_report.pdf` of the results will be generated.

Run `./test/test.py -h` and `./test/run.py -h` for detailed usage.

## Usage of Individual Scheme

```
# print the dependencies required to be installed
./src/<congestion-control>.py deps

# perform build commands for scheme
./src/<congestion-control>.py build

# run initialize commands after building and before running
./src/<congestion-control>.py init

# find running order for scheme
./src/<congestion-control>.py who_goes_first
```

Depending on the output about running order, run

```
# Receiver first
./src/<congestion-control>.py receiver
./src/<congestion-control>.py sender IP port
```

or

```
# Sender first
./src/<congestion-control>.py sender
./src/<congestion-control>.py receiver IP port
```
