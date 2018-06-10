#!/usr/bin/python

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.ticker import ScalarFormatter, NullFormatter
from collections import namedtuple, defaultdict
from functools import reduce
import numpy as np
from scipy import interpolate
from scipy.spatial import ConvexHull

Stats = namedtuple('Stats', ['util', 'delay'])

PARETO_COLOR = 'red'
PARETO_COLOR_LIGHT = '#FFAEB9'

CLOUD_DOTS = False

COLORS = {
    'abc': 'blue',
    'cubicpie': 'black',
    'cubiccodel': 'green',
    'cubic': '#b8860b',
    'bbr': 'red',
    'vegas': '#1f90ff',
    'sprout': '#800080',
    'verus': '#c71786',
    'copa': '#ff0dff',
    'pcc': '#b23c14',
    'ledbat': '#02b28c',
    'quic': '#6c8399'
}

NAMES = {
    'abc': 'ABC',
    'cubicpie': 'Cubic+Pie',
    'cubiccodel': 'Cubic+Codel',
    'cubic': 'Cubic',
    'bbr': 'BBR',
    'vegas': 'Vegas',
    'sprout': 'Sprout',
    'verus': 'Verus',
    'copa': 'Copa',
    'pcc': 'PCC',
    'ledbat': 'LEDBAT',
    'quic': 'QUIC'
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

def parse_file(filename, cloud, limit):
    stats = defaultdict(lambda: [])
    with open(filename) as f:
        for l in f:
            split = l.split(', ')
            if not len(split) > 6: continue # blank line
            proto = split[0]
            # 'limit' means only plot things from the original paper
            if limit and not proto in FIGURE2A_ORIGINAL: continue
            util = split[1]
            delay = split[6]
            if cloud:
                stats[proto].append(Stats(float(util), float(delay)))
            else: # only one point if no cloud
                stats[proto] = Stats(float(util), float(delay))
    return stats

def plot_cloud(stats):
    for proto, ss in stats.items():
        points = []

        for s in ss:
            if CLOUD_DOTS:
                ax1.plot(s.delay, s.util, 'o', markersize=1,
                    color=COLORS[proto], label=NAMES[proto])
            points.append((s.delay, s.util))

        # cloud background
        temp_points = list(points)
        points = []
        for p in temp_points:
            if not p[0] in [x[0] for x in points] and \
                not p[1] in [x[1] for x in points]:
                points.append(p)
        # only works with more than 3 pts and not same x or y coord for points
        if len(points) >= 3:
            # get border
            hull = ConvexHull(points)
            # https://stackoverflow.com/questions/33962717/interpolating-a-closed-curve-using-scipy
            x = np.array([points[v][0] for v in hull.vertices])
            y = np.array([points[v][1] for v in hull.vertices])
            x = np.r_[x, x[0]]
            y = np.r_[y, y[0]]
            # fit splines to x=f(u) and y=g(u), treating both as periodic. also note that s=0
            # is needed in order to force the spline fit to pass through all the input points.
            tck, u = interpolate.splprep([x, y], s=0, per=True)
            # evaluate the spline fits for 1000 evenly spaced distance values
            xi, yi = interpolate.splev(np.linspace(0, 1, 1000), tck)
            plt.fill(xi, yi, color=COLORS[proto], alpha=.4, edgecolor=None, linewidth=0)
        else:
            # if no cloud, small background
            x = np.mean(np.array([i.delay for i in ss]))
            y = np.mean(np.array([i.util for i in ss]))
            ax1.plot(x, y, 'o', markersize=4, color=COLORS[proto],
                alpha=.4, markeredgewidth=0, markeredgecolor=None)

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

def plot_reproduction_frontier(stats, cloud):
    x = []
    y = []
    for proto, s in stats.items():
        if proto == 'abc': continue # don't plot abc in frontier
        if cloud:
            x.append(np.mean(np.array([i.delay for i in s])))
            y.append(np.mean(np.array([i.util for i in s])))
        else:
            x.append(s.delay)
            y.append(s.util)

    plot_pareto_frontier(x, y, PARETO_COLOR_LIGHT, ':', maxY=False)

def plot_original(orig, stats, cloud):
    for proto, point in orig.items():
        s = stats[proto]
        ax1.plot(point[0], point[1], 'o', markersize=4, color=COLORS[proto])
        # text
        ax1.annotate(NAMES[proto], xy=point,
            xytext=(point[0] + 5, point[1]), color=COLORS[proto])
        if cloud:
            x = np.mean(np.array([i.delay for i in s]))
            y = np.mean(np.array([i.util for i in s]))
        else:
            x = s.delay
            y = s.util
        # line between our point and original
        ax1.plot([x, point[0]], [y, point[1]],'k-', color=COLORS[proto], linewidth=1)
        ax1.plot(x, y, 'o', markersize=4, markeredgewidth=1, markeredgecolor=COLORS[proto],
                markerfacecolor='None', label=NAMES[proto])

    plot_pareto_frontier(
        [point[0] for proto, point in orig.items() if proto != 'abc'],
        [point[1] for proto, point in orig.items() if proto != 'abc'],
        PARETO_COLOR, '--', maxY=False)

# https://matplotlib.org/2.0.2/users/annotations.html
def plot_better_box():
    bbox_props = dict(boxstyle='larrow,pad=1', fc='#cce5e5', ec='b', lw=1)
    t = plt.text(350, .4, 'Better', ha='center', va='center', rotation=-45,
            size=10, bbox=bbox_props)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='data_filename',
        help='csv file from which to read data', type=str)
    parser.add_argument(dest='plot_filename',
        help='svg file to save plot', type=str)
    parser.add_argument('-o', '--original-figure', default=None,
        help='original result to plot [2a, 2b]', type=str)
    parser.add_argument('-c', '--cloud', action='store_true', default=False,
        help='')
    parser.add_argument('-l', '--limit', action='store_true', default=False,
        help='')
    parser.add_argument('-b', '--better-box', action='store_true', default=False,
        help='')
    args = parser.parse_args()

    plt.xlabel('95th percentile packet delay (ms)')
    plt.ylabel('Utilization')
    plt.rcParams.update({'font.size': 10})
    # make axis ticks smaller so it doesn't get crowded
    rc('xtick', labelsize=10)
    rc('ytick', labelsize=10)

    ax1 = plt.subplot(111)
    ax1.set_ylim(.1, 1.0) # should be .3 for proper reproduction

    # log scale for x axis
    # use scalar not scientific format and
    # set major ticks to null because text is too crowded
    ax1.set_xscale('log')
    ax1.set_xticks([])
    ax1.xaxis.set_major_formatter(NullFormatter())
    ax1.xaxis.set_minor_formatter(ScalarFormatter())

    stats = parse_file(args.data_filename, args.cloud, args.limit)

    if args.cloud:
        plot_cloud(stats)

    for proto, s in stats.items():
        if args.cloud:
            x = np.mean(np.array([i.delay for i in s]))
            y = np.mean(np.array([i.util for i in s]))
        else:
            x = s.delay
            y = s.util
        ax1.plot(x, y, 'o', markersize=5, markeredgewidth=1, markeredgecolor=COLORS[proto],
                markerfacecolor='None', label=NAMES[proto])
        # annotate our point if not original figure
        if not args.original_figure or proto not in FIGURE2B_ORIGINAL:
            ax1.annotate(NAMES[proto], xy=(x, y),
                xytext=(x + 5, y), color=COLORS[proto])

    plot_reproduction_frontier(stats, args.cloud)

    # plot original result for comparison
    if args.original_figure:
        if args.original_figure not in ORIGINAL_FIGURES:
            raise Exception('No data found for that figure')
        orig = ORIGINAL_FIGURES[args.original_figure]
        orig = { p: orig[p] for p in orig if p in stats }
        plot_original(orig, stats, args.cloud)

    if args.better_box:
        plot_better_box()

    # save plot to file
    pf = args.plot_filename
    if not pf.endswith('.svg'): pf += '.svg'
    plt.savefig(pf)
