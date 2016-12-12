#! /bin/bash
mkdir -p ~/.ssh
ssh-keygen -q -N "" -f ~/.ssh/id_rsa < /dev/zero
cat ~/id_rsa.pub >> ~/.ssh/authorized_keys
