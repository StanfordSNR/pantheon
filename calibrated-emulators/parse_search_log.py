#!/usr/bin/env python

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('search_log')
    parser.add_argument('order')
    args = parser.parse_args()

    order = args.order.split(',')
    for i in range(len(order)):
        order[i] = order[i].strip()

    search_log = open(args.search_log)

    min_loss = 500.0
    min_items = None

    sec_loss = 500.0
    sec_items = None

    while True:
        line = search_log.readline()
        if not line:
            break

        items = line.split(',')

        col = 0

        candidate_items = []
        for x in order:
            if x == 'bandwidth':
                candidate_items.append(items[col].split('=')[1])
            elif x == 'delay':
                candidate_items.append(items[col].split('=')[1])
            elif x == 'uplink_loss':
                candidate_items.append(items[col].split('=')[1])
            elif x == 'uplink_queue':
                candidate_items.append(items[col].split('=')[1])

            col += 1

        tput_loss = items[col].split('=')[1]
        candidate_items.append(tput_loss)
        col += 1
        delay_loss = items[col].split('=')[1]
        candidate_items.append(delay_loss)
        col += 1
        overall_loss = items[col].split('=')[1]
        candidate_items.append(overall_loss)

        if float(overall_loss) < min_loss:
            old_min_loss = min_loss
            old_min_items = min_items

            min_loss = float(overall_loss)
            min_items = candidate_items

            sec_loss = old_min_loss
            sec_items = old_min_items
        elif float(overall_loss) < sec_loss:
            sec_loss = float(overall_loss)
            sec_items = candidate_items

    search_log.close()

    print args.order + ", tput_loss, delay_loss, overall_loss"
    print min_items
    print sec_items


if __name__ == '__main__':
    main()
