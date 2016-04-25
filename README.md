[![Build Status](https://travis-ci.org/StanfordLPNG/pantheon.svg?branch=master)](https://travis-ci.org/StanfordLPNG/pantheon)

# Pantheon of Congestion Control

## Make

1. Clone this repository

  ```
  git clone https://github.com/StanfordLPNG/pantheon.git
  ```

2. Get submodules:

  ```
  $ git submodule init
  $ git submodule update
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
  $ python congestion_control_name.py setup 
  $ python congestion_control_name.py receiver 
  $ python congestion_control_name.py sender IP port 
  ```

* Exception: to run QUIC,

  ```
  $ cd panthon/src
  $ python quic.py setup 
  $ python quic.py sender 
  $ python quic.py receiver IP port 
  ```

* Run tests:

  ```
  $ cd pantheon/test
  $ python test.py congestion_control_name
  ```
