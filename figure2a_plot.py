#!/usr/bin/python

import matplotlib.pyplot as plt
from collections import namedtuple

Stats = namedtuple('Stats', ['util', 'delay'])

COLORS = {
    'abc': 'blue',
    'cubicpie': 'black',
    'cubiccodel': 'green',
    'cubic': 'brown'
}

NAMES = {
    'abc': 'ABC',
    'cubicpie': 'Cubic+Pie',
    'cubiccodel': 'Cubic+Codel',
    'cubic': 'Cubic'
}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', default=None,
        help='csv file from which to read data', type=str)
    args = parser.parse_args()

    stats = dict()

    if args.filename:
        with open(args.filename) as f:
            for l in f:
                proto, util, delay = l.split(', ')
                stats[proto] = Stats(float(util), float(delay))
    else:
        # use static stats
        stats = {
            'abc': Stats(util=.8926174496644295, delay=182.0),
            'cubicpie': Stats(util=.5218120805369128, delay=160.0),
            'cubiccodel': Stats(util=.6057046979865772, delay=142.0),
            'cubic': Stats(util=.9563758389261746, delay=896.0)
        }

    plt.xlabel('95th percentile packet delay (ms)')
    plt.ylabel('Utilization')

    for proto, s in stats.items():
        plt.plot(s.delay, s.util, 'o', color=COLORS[proto], label=NAMES[proto])
        plt.annotate(NAMES[proto], xy=(s.delay, s.util),
            xytext=(s.delay + 15, s.util), color=COLORS[proto])

    plt.show()
    plt.savefig('figure2a.png')
