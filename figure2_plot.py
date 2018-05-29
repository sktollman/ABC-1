#!/usr/bin/python

import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.ticker import ScalarFormatter, NullFormatter
from collections import namedtuple, defaultdict
from functools import reduce

Stats = namedtuple('Stats', ['util', 'delay'])

PARETO_COLOR = 'red'
PARETO_COLOR_LIGHT = '#FFAEB9'

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

FIGURE2A_ORIGINAL = {
    'abc': (191.95834358517678, 0.8895608259285301),
    'bbr': (486.8920433391686, 0.9399028319376079),
    'cubic': (445.5895460340233, 0.9801764367448698),
    'cubiccodel': (177.88015620661164, 0.6188327047241577),
    'cubicpie': (153.80228344469558, 0.5282170939078181),
    'sprout': (174.8117213747123, 0.3984465895288627),
    'vegas': (341.5402884053896, 0.9113756951991305),
    'verus': (354.68196232307116, 0.8627117560570223)
}
FIGURE2B_ORIGINAL = {
    'abc': (194.61469364942175, 0.8567136150234742),
    'bbr': (579.8963509590329, 0.9323004694835679),
    'cubic': (557.3238874983415, 0.9743661971830986),
    'cubiccodel': (207.58455812573303, 0.6207511737089202),
    'cubicpie': (172.76170142715284, 0.5510798122065728),
    'sprout': (178.69145410543587, 0.38215962441314555),
    'vegas': (591.5231350767796, 0.9296713615023473),
    'verus': (419.5871922555574, 0.8218779342723004)
}
ORIGINAL_FIGURES = { '2a': FIGURE2A_ORIGINAL, '2b': FIGURE2B_ORIGINAL }

# based off of https://sirinnes.wordpress.com/2013/04/25/pareto-frontier-graphic-via-python/
def plot_pareto_frontier(Xs, Ys, color, linestyle, maxX=True, maxY=True):
    '''Pareto frontier selection process'''
    sorted_list = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxY)
    pareto_front = [sorted_list[0]]
    for pair in sorted_list[1:]:
        if pair[0] >= pareto_front[-1][0] and pair[1] >= pareto_front[-1][1]:
            pareto_front.append(pair)

    '''Plotting process'''
    pf_X = [pair[0] for pair in pareto_front]
    pf_Y = [pair[1] for pair in pareto_front]
    plt.plot(pf_X, pf_Y, color=color, linestyle=linestyle, linewidth=1)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data-filename', default=None,
        help='csv file from which to read data', type=str, nargs='+')
    parser.add_argument('-p', '--plot-filename', default=None,
        help='svg file to save plot', type=str)
    parser.add_argument('-o', '--original-figure', default=None,
        help='original result to plot [2a, 2b]', type=str)
    args = parser.parse_args()

    stats = dict()

    if args.data_filename:
        temp_stats = defaultdict(lambda: list())
        for fn in args.data_filename:
            with open(fn) as f:
                for l in f:
                    proto, util, delay, throughput, power = l.split(', ')
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

    for proto, s in stats.items():
        ax1.plot(s.delay, s.util, 'o', markersize=7, markeredgewidth=1, markeredgecolor=COLORS[proto],
            markerfacecolor='None', label=NAMES[proto])
        ax1.annotate(NAMES[proto], xy=(s.delay, s.util),
            xytext=(s.delay + 15, s.util), color=COLORS[proto])

    plot_pareto_frontier(
        [s.delay for proto, s in stats.items() if proto != 'abc'],
        [s.util for proto, s in stats.items() if proto != 'abc'],
        PARETO_COLOR_LIGHT, ':', maxY=False)

    # line between original and reproduction results
    if args.original_figure:
        if args.original_figure not in ORIGINAL_FIGURES:
            raise Exception('No data found for that figure')
        orig = ORIGINAL_FIGURES[args.original_figure]

        for proto, point in orig.items():
            if proto not in stats: continue
            s = stats[proto]
            ax1.plot(point[0], point[1], 'o', markersize=7, color=COLORS[proto])
            ax1.plot([s.delay, point[0]], [s.util, point[1]],'k-', color=COLORS[proto])

        plot_pareto_frontier(
            [point[0] for proto, point in orig.items() if proto != 'abc'],
            [point[1] for proto, point in orig.items() if proto != 'abc'],
            PARETO_COLOR, '--', maxY=False)

    # save plot to file
    if args.plot_filename:
        pf = args.plot_filename if args.plot_filename.endswith('.svg') else '{}.svg'.format(args.plot_filename)
        plt.savefig(pf)

    plt.show()
