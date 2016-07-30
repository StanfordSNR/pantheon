[![Build Status](https://travis-ci.org/StanfordLPNG/pantheon.svg?branch=master)](https://travis-ci.org/StanfordLPNG/pantheon)

# Pantheon of Congestion Control

## Make

1. Clone this repository

  ```
  git clone https://github.com/StanfordLPNG/pantheon.git
  ```

2. Get submodules:

  ```
  git submodule update --init
  ```

3. Build pantheon:

  ```
  ./autogen.sh
  ./configure
  make -j
  ```

## Usage

### To run a specific congestion control scheme:
* Perform local setup/build commands for scheme

  ```
  cd test/
  ./setup.py [congestion-control-name]
  ```

* Find running order for scheme

  ```
  cd src/
  ./[congestion-control-name].py who_goes_first
  ```
* Depending on the output about running order, run

  ```
  # Receiver first
  ./[congestion-control-name].py receiver
  ./[congestion-control-name].py sender IP port
  ```

  or

  ```
  # Sender first
  ./[congestion-control-name].py sender
  ./[congestion-control-name].py receiver IP port
  ```

* To test a scheme locally over emulated mahimahi link:

  ```
  cd test/
  ./setup.py congestion-control-name
  ./test_locally.py congestion-control-name
  ```
