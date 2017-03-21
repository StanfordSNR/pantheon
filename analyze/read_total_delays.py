#!/usr/bin/env python

def main():
    with open('total_delays') as f:
        line = f.readline().split()
        print min(map(float, line))


if __name__ == '__main__':
    main()
