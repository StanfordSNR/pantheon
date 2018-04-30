#!/bin/sh

echo -n 'branch: '
git rev-parse --abbrev-ref @ | head -c -1
echo -n ' @ '
git rev-parse @
git submodule foreach --quiet 'echo $path @ `git rev-parse @`; git status -s --untracked-files=no --porcelain'
