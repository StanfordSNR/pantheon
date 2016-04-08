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
  or clone this project with the --recursive option

## Usage

The executable files can be found in the 'src' folder at the top
level. Run 'server.py' and 'client.py' in two shells
respectively, specifying a congestion control option along with
additional arguments.

Example:

* To use default TCP as congestion control:
  ```
  $ python server.py TCP PORT
  $ python client.py TCP HOST PORT
  ```
