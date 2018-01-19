#!/usr/bin/env python

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('search_log')
    args = parser.parse_args()

    search_log = open(args.search_log)

    min_loss = 100.0
    min_items = None

    sec_loss = 100.0
    sec_items = None

    below_loss = 30.0
    below_items = []

    while True:
        line = search_log.readline()
        if not line:
            break

        items = line.split(',')

        bw = items[0].split('=')[1]
        delay = items[1].split('=')[1]
        uplink_queue = items[2].split('=')[1]
        #uplink_loss = items[3].split('=')[1]
        #downlink_loss = items[4].split('=')[1]
        tput_loss = items[3].split('=')[1]
        delay_loss = items[4].split('=')[1]
        overall_loss = items[5].split('=')[1]

        if float(overall_loss) < min_loss:
            old_min_loss = min_loss
            old_min_items = min_items

            min_loss = float(overall_loss)
            min_items = (bw, delay, uplink_queue, #uplink_loss, downlink_loss,
                         tput_loss, delay_loss, overall_loss)

            sec_loss = old_min_loss
            sec_items = old_min_items
        elif float(overall_loss) < sec_loss:
            sec_loss = float(overall_loss)
            sec_items = (bw, delay, uplink_queue, #uplink_loss, downlink_loss,
                         tput_loss, delay_loss, overall_loss)

        if float(overall_loss) < 30.0:
            below_items.append((bw, delay, uplink_queue, tput_loss, delay_loss, overall_loss))

    search_log.close()

    # print 'bw, delay, uplink_queue, uplink_loss, downlink_loss, tput_loss, delay_loss, overall_loss'
    print 'bw, delay, uplink_queue, tput_loss, delay_loss, overall_loss'
    print min_items
    print sec_items

    for item in below_items:
        print item


if __name__ == '__main__':
    main()
