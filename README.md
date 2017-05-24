[![Build Status](https://travis-ci.org/StanfordSNR/pantheon.svg?branch=master)](https://travis-ci.org/StanfordSNR/pantheon)

# Disclaimer:
This is research software. Our scripts will write to
the file system in the pantheon folder and in `/tmp/pantheon-tmp`.
We never run third party programs as root, but we cannot guarantee they will
never try to escalate privilege to root.

Run at your own risk. Feel free to contact our mailing list:
`the name of this repository`@cs.stanford.edu

# Pantheon of Congestion Control
The Pantheon has wrappers for many popular and research congestion control
schemes. It allows them to run over a common interface and has tools to
benchmark and compare their performance.
Pantheon tests can be run locally over an emulated link using
[mahimahi](http://mahimahi.mit.edu/) or over the internet to a remote machine.

## Preparation
Many of the tools and programs run by the Pantheon are git submodules in the
`third_party` folder. To clone this repository, including submodules, run:

```
git clone --recursive https://github.com/StanfordSNR/pantheon.git
```

To add submodules after cloning, run:

```
git submodule update --init
```

## Dependencies
We provide a handy script `install_deps.py` to install globally required
dependencies. But you may want to check the script and install these
dependencies by yourself.

For those dependencies required by each congestion control scheme `<cc>`,
run `src/<cc>.py deps` to print a dependency list. Again you could install
them by yourself. Alternatively, run

```
test/setup.py --install-deps (--all | --schemes "<cc1> <cc2> ...")
```

to install dependencies required by all schemes or a list of schemes separated
by spaces.

## Setup
After installing dependencies, run

```
test/setup.py [--setup] [--all | --schemes "<cc1> <cc2> ..."]
```

to set up schemes. `--setup` is only required the first time when running these
schemes. Otherwise, `test/setup.py` is required to be run only every time after
reboots (without `--setup`).

## Running the Pantheon
To test schemes in emulated networks locally, run

```
test/test.py local (--all | --schemes "<cc1> <cc2> ...")
```

To test schemes over the internet to remote machine, run

```
test/test.py remote (--all | --schemes "<cc1> <cc2> ...") HOSTADDR:PANTHEON-DIR
```

Run `test/test.py local -h` and `test/test.py remote -h` for detailed
usage and additional optional arguments, such as multiple flows, running time,
arbitrary set of mahimahi shells for local tests, data sender side for
remote tests, etc.

## Pantheon analysis
To analyze test results, run

```
analysis/analyze.py [--data-dir DIR]
```

It will analyze the logs saved by `test/test.py`, then generate charts and
`pantheon_report.pdf`.

The directory to save data is `test/data` by default,
but it can be set by `--data-dir` on `test/test.py` and `analysis/analyze.py`.

## Running a single congestion control scheme
All the available schemes can be found in `src/config.yml`. To run a single
congestion control scheme, first follow the **Dependencies** section to install
required dependencies.

At the first time testing it, run `src/<cc>.py setup`
to perform setup that is persistent across reboots, such as compilation,
generating or downloading files to send, etc. Then run
`src/<cc>.py setup_after_reboot`, which has to be run again every time after
reboots. In fact, `test/setup.py [--setup]` performs `setup_after_reboot` by
default, and runs `setup` on schemes when `--setup` is given.

Next, find running order for scheme:
```
./<cc>.py run_first
```

Depending on the output of `run_first`, run

```
# Receiver first
./<cc>.py receiver
./<cc>.py sender IP port
```

or

```
# Sender first
./<cc>.py sender
./<cc>.py receiver IP port
```

Run `src/<cc>.py -h` for detailed usage of the common interface.
