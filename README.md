[![Build Status](https://travis-ci.org/StanfordLPNG/pantheon.svg?branch=master)](https://travis-ci.org/StanfordLPNG/pantheon)

# Pantheon of Congestion Control

## Make

1. Clone this repository

  ```
  git clone https://github.com/StanfordLPNG/pantheon.git
  ```

2. Get submodules:

  ```
  $ git submodule update --init
  ```

3. Install dependencies:

  ```
  $ ./install_deps.sh
  ```

4. Build third-party repositories:

  ```
  $ ./build_third_party.sh
  ```

5. Build pantheon:

  ```
  $ ./autogen.sh
  $ ./configure
  $ make -j
  ```
## Usage

* General Usage:

  ```
  $ cd panthon/src
  $ ./congestion-control-name.py setup
  ```

  Depending on the output about running order, run

  ```
  # Receiver first
  $ ./congestion-control-name.py receiver
  $ ./congestion-control-name.py sender IP port
  ```

  or

  ```
  # Sender first
  $ ./congestion-control-name.py sender
  $ ./congestion-control-name.py receiver IP port
  ```

* Run tests:

  ```
  $ cd pantheon/test
  $ ./test.py congestion-control-name
  ```
