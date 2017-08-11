#!/usr/bin/env python


def main():
    history = open('/home/francisyyan/pantheon/test/cwnd-guess/history')

    ret = {}
    while True:
        line = history.readline()
        if not line:
            break

        bw, owd, cwnd, tput, delay, score = line.split()
        bw = int(bw)
        owd = int(owd)
        cwnd = int(cwnd)
        tput = float(tput)
        delay = float(delay)
        score = float(score)

        if bw not in ret:
            ret[bw] = {}

        if owd not in ret[bw]:
            ret[bw][owd] = (cwnd, score)
        else:
            if score > ret[bw][owd][1]: # and (tput / bw) > 0.9:
                ret[bw][owd] = (cwnd, score)

    history.close()

    best_cwnd = open('/home/francisyyan/pantheon/test/cwnd-guess/best_cwnd', 'w')
    best_cwnd.write('bw\tmm-delay\tcwnd\n')

    for bw in sorted(ret.keys()):
        for owd in sorted(ret[bw].keys()):
            best_cwnd.write('%s\t%s\t%s\n' % (bw, owd, ret[bw][owd][0]))

    best_cwnd.close()


if __name__ == '__main__':
    main()
