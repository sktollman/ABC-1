#!/usr/bin/python

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from collections import defaultdict, OrderedDict

COLORS = {
    'abc': '#3d68c5',
    'cubiccodel': '#449331',
    'cubic': '#f29d38',
    'bbr': '#cb4727',
    'vegas': '#4298c2',
    'sprout': '#8c2294',
    'verus': '#cd5177',
}

NAMES = {
    'abc': 'ABC',
    'cubiccodel': 'Cubic+Codel',
    'cubic': 'Cubic',
    'bbr': 'BBR',
    'vegas': 'Vegas',
    'sprout': 'Sprout',
    'verus': 'Verus',
}

SHAPES = {
    'abc': ('o', 8),
    'cubiccodel': ('D', 5),
    'cubic': ('s', 4),
    'bbr': ('^', 5),
    'vegas': ('x', 4),
    'sprout': ('*', 5),
    'verus': ('p', 6),
}

TRACES = [ # maintain same ordering as original figure
    'Verizon-LTE-short.up',
    'Verizon-LTE-driving.up',
    'TMobile-LTE-driving.up',
    'ATT-LTE-driving.up',
    'Verizon-LTE-short.down',
    'Verizon-LTE-driving.down',
    'TMobile-LTE-driving.down',
    'ATT-LTE-driving.down'
]

def parse_file(filename):
    stats = defaultdict(lambda: [])
    with open(filename) as f:
        for l in f:
            split = l.split(', ')
            proto = split[0]
            util = split[1]
            delay = split[6]
            trace = split[7]
            power = 1000 * float(util) / float(delay)
            if proto in SHAPES:
                stats[trace].append((proto, float(power)))
    return stats

def plot_data(ax1, stats, traces):
    all_for_proto = defaultdict(lambda: [])
    for trace in traces:
        if trace not in stats: continue
        results = stats[trace]
        for proto, power in results:
            power = float(power)
            all_for_proto[proto].append(power)
            shape, size = SHAPES[proto]
            ax1.plot(traces.index(trace), power, shape,
                markersize=size, color=COLORS[proto], label=NAMES[proto])

    for proto, results in all_for_proto.items():
        avg = sum(results) / float(len(results))
        shape, size = SHAPES[proto]
        ax1.plot(len(traces), avg, shape, markersize=size,
            color=COLORS[proto], label=NAMES[proto])

def update_layout(ax1, stats, traces):
    ax1.set_xlim(-.5, len(stats) + .5)
    ax1.set_ylim(0, 6.0)
    ax1.set_yticks([0, 2, 4, 6])
    ax1.grid(axis='y')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    # remove y ticks and set smaller font to match paper
    for tic in ax1.yaxis.get_major_ticks():
        tic.label.set_fontsize(6)
        tic.tick1On = tic.tick2On = False
    ax1.set_xticks(list(range(len(traces) + 1)))
    xlabels = traces + ['AVERAGE']
    ax1.set_xticklabels(xlabels, rotation=25, horizontalalignment='right',
        color='#707070')
    for tic in ax1.xaxis.get_major_ticks():
        tic.tick1On = tic.tick2On = False
    # remove duplicates and alphabetize
    # https://stackoverflow.com/questions/13588920/stop-matplotlib-repeating-labels-in-legend
    handles, labels = plt.gca().get_legend_handles_labels()
    # https://stackoverflow.com/questions/22263807/how-is-order-of-items-in-matplotlib-legend-determined
    by_label = OrderedDict(sorted(zip(labels, handles), key=lambda t: t[0]))
    plt.legend(by_label.values(), by_label.keys(), frameon=False,
        loc='upper center', bbox_to_anchor=(0.5, 1.1), fontsize='x-small',
        edgecolor=None, ncol=len(labels), handletextpad=0, columnspacing=.5)

    plt.tight_layout() # makes space for bottom x-labels

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='data_filename',
        help='csv file from which to read data', type=str)
    parser.add_argument(dest='plot_filename',
        help='svg file to save plot', type=str)
    args = parser.parse_args()

    stats = parse_file(args.data_filename)
    traces = list(filter(lambda t: t in stats, TRACES))

    plt.ylabel('Power')
    plt.rcParams.update({'font.size': 14,
        'text.color': '#808080', 'lines.color': 'gray'})

    ax1 = plt.subplot(111)

    plot_data(ax1, stats, traces)
    update_layout(ax1, stats, traces)

    # save plot to file
    pf = args.plot_filename
    if not pf.endswith('.svg'): pf += '.svg'
    plt.savefig(pf)
