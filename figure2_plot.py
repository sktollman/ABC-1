#!/usr/bin/python

import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.ticker import ScalarFormatter, NullFormatter
from collections import namedtuple, defaultdict
from functools import reduce

Stats = namedtuple('Stats', ['util', 'delay'])

COLORS = {
    'abc': 'blue',
    'cubicpie': 'black',
    'cubiccodel': 'green',
    'cubic': '#b8860b',
    'bbr': 'red',
    'vegas': '#1f90ff',
    'sprout': '#800080',
    'verus': '#c71786'
}

NAMES = {
    'abc': 'ABC',
    'cubicpie': 'Cubic+Pie',
    'cubiccodel': 'Cubic+Codel',
    'cubic': 'Cubic',
    'bbr': 'BBR',
    'vegas': 'Vegas',
    'sprout': 'Sprout',
    'verus': 'Verus'
}

# based off of https://sirinnes.wordpress.com/2013/04/25/pareto-frontier-graphic-via-python/
def plot_pareto_frontier(Xs, Ys, maxX=True, maxY=True):
    '''Pareto frontier selection process'''
    sorted_list = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxY)
    pareto_front = [sorted_list[0]]
    for pair in sorted_list[1:]:
        if pair[0] >= pareto_front[-1][0] and pair[1] >= pareto_front[-1][1]:
            pareto_front.append(pair)

    '''Plotting process'''
    pf_X = [pair[0] for pair in pareto_front]
    pf_Y = [pair[1] for pair in pareto_front]
    plt.plot(pf_X, pf_Y, color='red', linestyle='dashed', linewidth=1)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-filename', default=None,
        help='csv file from which to read data', type=str, nargs='+')
    parser.add_argument('--plot-filename', default=None,
        help='svg file to save plot', type=str)
    args = parser.parse_args()

    stats = dict()

    if args.data_filename:
        temp_stats = defaultdict(lambda: list())
        for fn in args.data_filename:
            with open(fn) as f:
                for l in f:
                    proto, util, delay = l.split(', ')
                    temp_stats[proto].append(Stats(float(util), float(delay)))
        for proto, stats_list in temp_stats.items():
            avg_util = reduce(lambda x, y: x + y,
                map(lambda x: x.util, stats_list)) / float(len(stats_list))
            avg_delay = reduce(lambda x, y: x + y,
                map(lambda x: x.delay, stats_list)) / float(len(stats_list))
            stats[proto] = Stats(avg_util, avg_delay)

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
    plt.rcParams.update({'font.size': 14})
    # make axis ticks smaller so it doesn't get crowded
    rc('xtick', labelsize=10)
    rc('ytick', labelsize=10)

    ax1 = plt.subplot(111)
    ax1.set_ylim(.3, 1.0)

    # log scale for x axis
    # use scalar not scientific format and
    # set major ticks to null because text is too crowded
    ax1.set_xscale('log')
    ax1.set_xticks([])
    ax1.xaxis.set_major_formatter(NullFormatter())
    ax1.xaxis.set_minor_formatter(ScalarFormatter())

    Xs = []
    Ys = []
    for proto, s in stats.items():
        if proto != 'abc':
            Xs.append(s.delay)
            Ys.append(s.util)
        ax1.plot(s.delay, s.util, 'o', color=COLORS[proto], label=NAMES[proto])
        ax1.annotate(NAMES[proto], xy=(s.delay, s.util),
            xytext=(s.delay + 15, s.util), color=COLORS[proto])

    plot_pareto_frontier(Xs, Ys, maxY=False)

    # save plot to file
    if args.plot_filename:
        pf = args.plot_filename if args.plot_filename.endswith('.svg') else '{}.svg'.format(args.plot_filename)
        plt.savefig(pf)

    plt.show()
