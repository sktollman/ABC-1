#
# Generates full-length fix-bandwidth
# mahi traces files. 
#

import argparse

def print_mahi_trace(length, bw):
    for i in range(1, length+1):
        for _ in range(bw / 12):
            print(i)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--length',
            type=int,
            required=True,
            help="(ms) length of trace")

    # TODO: if needed, extend to
    #       arbitrary bandwidths.
    parser.add_argument('--bw',
            type=int,
            required=True,
            help="can be 12, 24, 36, 48")

    args = parser.parse_args()

    print_mahi_trace(args.length, args.bw)
