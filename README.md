[![Build Status](https://travis-ci.org/StanfordSNR/pantheon.svg?branch=master)](https://travis-ci.org/StanfordSNR/pantheon)

# Pantheon of Congestion Control
The Pantheon contains wrappers for many popular practical and research
congestion control schemes. The Pantheon enables them to run on a common
interface, and has tools to benchmark and compare their performances.
Pantheon tests can be run locally over emulated links using
[mahimahi](http://mahimahi.mit.edu/) or over the Internet to a remote machine.

Our website is <http://pantheon.stanford.edu>, where you can find more
information about Pantheon, including supported schemes, our real-world
experiment results so far, and how to get involved.

To discuss and talk about Pantheon-related topics and issues,

Feel free to contact our mailing list:
`pantheon-stanford <at> googlegroups <dot> com`.

## Disclaimer
This is research software. Our scripts will write to the file system in the
`pantheon` folder and `/tmp/pantheon-tmp`. We never run third party programs
as root, but we cannot guarantee they will never try to escalate privilege to
root.

You might want to install dependencies and run the setup on your own, because
our handy scripts will install packages and perform some system-wide settings
(e.g., enable IP forwarding, `modprobe tcp_vegas`) as root. Please run at your
own risk.

## Preparation
To clone this repository, run:

```
git clone https://github.com/StanfordSNR/pantheon.git
```

Many of the tools and programs run by the Pantheon are git submodules in the
`third_party` folder. To add submodules after cloning, run:

```
git submodule update --init --recursive  # or ./fetch_submodules.sh
```

## Dependencies
We provide a handy script `install_deps.sh` to install globally required
dependencies. But you may want to inspect the contents of this script and
install these dependencies yourself.

For those dependencies required by each congestion control scheme `<cc>`,
run `src/<cc>.py deps` to print a dependency list. Again, you could install
them yourself. Alternatively, run

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

to set up supported congestion control schemes. `--setup` is only required the
first time when running these schemes. Otherwise, `test/setup.py` is
required to be run only every reboot (without `--setup`).

## Running the Pantheon
To test schemes in emulated networks locally, run

```
test/test.py local (--all | --schemes "<cc1> <cc2> ...")
```

To test schemes over the Internet to remote machine, run

```
test/test.py remote (--all | --schemes "<cc1> <cc2> ...") HOST:PANTHEON-DIR
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
a report called `pantheon_report.pdf`.

The directory to save data is `test/data` by default,
but it can be set by `--data-dir` on `test/test.py` and `analysis/analyze.py`.

## Running a single congestion control scheme
All the available schemes can be found in `src/config.yml`. To run a single
congestion control scheme, first follow the **Dependencies** section to install
the  required dependencies.

During the first time testing, run `src/<cc>.py setup`
to perform the setup persistent across reboots, such as compilation,
generating or downloading files to send, etc. Then run
`src/<cc>.py setup_after_reboot`, which has to be run again every time after
a reboot. In fact, `test/setup.py [--setup]` performs `setup_after_reboot` by
default, and runs `setup` on schemes when `--setup` is given.

Next, execute the following command to find the running order for a scheme:
```
src/<cc>.py run_first
```

Depending on the output of `run_first`, run

```
# Receiver first
src/<cc>.py receiver port
src/<cc>.py sender IP port
```

or

```
# Sender first
./<cc>.py sender port
./<cc>.py receiver IP port
```

Run `src/<cc>.py -h` for detailed usage of the common interface.

## How to add your own congestion control
Adding your own congestion control to Pantheon is easy! Just follow these
steps:

1. Fork this repository.

2. Add your congestion control repository as a submodule to `pantheon`:

   ```
   git submodule add <your-cc-repo-url> third_party/<your-cc-name>
   ```

   It would be even better if you could also add `ignore = dirty` to
   `.gitmodules` under your submodule.

3. In `src`, read `example.py` and create your own `<your-cc-name>.py`.
   Make sure the sender and receiver run longer than 30 seconds
   (preferably longer than 60 seconds); you could also leave
   them running forever without the need to kill them.

4. Add your scheme to `src/config.yml` along with settings of
   `friendly_name`, `color` and `marker`, so that `test/test.py` is able to
   find your scheme and `analysis/analyze.py` is able to generate plots with
   your specified settings.

5. Add your scheme to `SCHEMES` in `.travis.yml` for continuous testing.

6. Send us a pull request and that's it, you're in the Pantheon!
