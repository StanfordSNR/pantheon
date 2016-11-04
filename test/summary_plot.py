#!/usr/bin/env python

import os
import sys
from os import path
from parse_arguments import parse_arguments


def main():
    args = parse_arguments(path.basename(__file__))


if __name__ == '__main__':
    main()
