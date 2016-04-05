# Pantheon of Congestion Control

## Make

1. Get submodules:

  ```
  $ git submodule init
  $ git submodule update
  ```

  or clone this project with the --recursive option

2. Run the following commands to make:

  ```
  $ mkdir build
  $ cd build
  $ cmake .. && make
  ```

## Usage

The executable files can be found in the 'bin' folder at the top level. Run 'server' and 'client' in two shells respectively, specifying a congestion control mechanism along with additional arguments. 

Example:

* To use default TCP as congestion control:

  ```
  $ ./server TCP
  $ ./client TCP 0.0.0.0
  ```

* To use LEDBAT as congestion control:

  ```
  $ ./server LEDBAT
  $ ./client LEDBAT 0.0.0.0
  ```

