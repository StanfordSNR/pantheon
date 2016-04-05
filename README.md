# pantheon
Pantheon of Congestion Control

1. To get submodules:
$ git submodule init
$ git submodule update

or clone this project with the --recursive option

2. Run the following commands to make:
$ mkdir build
$ cd build
$ cmake .. && make
$ cd ../bin

you will find two executable files 'client' and 'server'

3. Run 'client' and 'server' in two shells:
Example: to use default TCP as congestion control,
$ ./server TCP
$ ./client TCP 0.0.0.0
