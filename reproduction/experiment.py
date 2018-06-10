#!/usr/bin/python

#
# Runs experiments to generate the figures in
# ABC HotNets 2017 paper.
#

from subprocess import Popen
from collections import namedtuple
from protocols.cc_protocol import CCProtocol
from protocols.utils import get_protocol

import os
import argparse
import time
import sys
import shlex

TRACE_DIR = '~/ABC-1/mahimahi/traces/'
BW_TRACE_DIR = '~/ABC-1/reproduction/traces/'

STATIC_BW_FIXED = 'bw48-fixed.mahi'
STATIC_BW_VARIABLE = 'bw48-variable.mahi'

# Becomes populated with experiment results for figure 2.
Stats = namedtuple(
        'Stats',
        ['util', 'delay', 'throughput', 'power', \
         'queuing_delay', 'per_packet_delay', 'uplink_trace', 'downlink_trace']
)
stats = []

def retrieve_and_print_stats(cc_proto, rtt, uplink_trace, downlink_trace):
    """ Prints results for a figure 1, 2 - type experiment.

    Additionally, saves statistics to the "stats" global
    variable.
    """
    proto_name = cc_proto.config['name']
    if os.path.isfile(cc_proto.results_file_path):
        with open(cc_proto.results_file_path) as f:
            lines = f.readlines()
            avg_capacity = float(lines[0].split(' ')[2])
            avg_throughput = float(lines[1].split(' ')[2])
            queuing_delay = float(lines[2].split(' ')[5])
            signal_delay = float(lines[3].split(' ')[4])

            utilization = avg_throughput / avg_capacity

            per_packet_delay = rtt + queuing_delay
            power_score = 1000 * avg_throughput / float(signal_delay)

            stats_bundle = {}

            stats_bundle[proto_name] = Stats(
                    utilization, signal_delay, avg_throughput,
                    power_score, queuing_delay, per_packet_delay,
                    uplink_trace, downlink_trace
            )

            stats.append(stats_bundle)

            print("\n  ~~ Results for protocol: %s ~~" % proto_name)
            print("\tutilization: %s%%" % str(round(100 * utilization, 2)))
            print("\tthroughput: %s Mbps" % str(avg_throughput))
            print("\tsignal delay: %s ms" % str(signal_delay))
            print("\tqueuing delay: %s ms" % str(queuing_delay))
            print("\tpower score: %s" % str(power_score))
            print("\tavg capacity: %s Mbps" % str(avg_capacity))
            print("\tper-packet delay: %s ms\n" % str(per_packet_delay))

    else:
        print("No results found for proto %s at path: %s\n"
                % (proto_name, cc_proto.results_file_path))

def run_cmds(cmds, verbose=False):
    """Runs the commands in CMDS.

    Runs "prep" commands in the background, and
    all other commands sequentially.  Cleans up
    lingering processes returned by Popen call.

    Args:
        cmds: (OrderedDict) Maps descriptions of commands to
              lists of command strings to run.
    """
    processes = []
    home = os.path.expanduser('~')
    devnull = open(os.devnull, 'w')
    try:
        for c_type in cmds:
            for c in cmds[c_type]:
                if not c: continue

                # Need full pathname for home
                c = c.replace('~', home)

                if verbose:
                    print("$ %s" % ' '.join(c.split(' ')))

                # Ugly hack, I'm sorry. Don't know how else
                # to respect a sleep between commands.
                if c.startswith('sleep '):
                    time.sleep(int(c.split(' ')[-1]))
                    continue

                if c_type == "prep":
                    proc = Popen(
                            shlex.split(c), stdout=devnull, stderr=devnull
                            )
                else:
                    proc = Popen(
                            c, shell=True, stdout=devnull,
                            stderr=devnull
                            )

                processes.append(proc)

                # We run all 'prep' commands in the background,
                # and wait for everything else to finish.
                if c_type != 'prep':
                    proc.wait()

    except KeyboardInterrupt:
        pass

    devnull.close()

    # Attempt to kill all lingering processes
    for p in processes:
        if p:
            try:
                p.kill()
            except OSError:
                pass

def make_bw_file(ref_trace, bw_trace, bw):
    """Generates bw*.mahi file at bw_trace to match
    the exact length of ref_trace, with bw Mbps bandwidth.
    """
    if bw % 12 != 0:
        raise ValueError("Can only create files of bandwidth multiples of 12")

    length = 0
    with open(os.path.expanduser(ref_trace), 'r') as f:
        for line in f:
            pass
        length = int(line.strip())

    with open(os.path.expanduser(bw_trace), 'w') as f:
        for i in range(1, length+1):
            for _ in range(bw / 12):
                f.write("%d\n" % i)

def run_fig1_exp(schemes, traces, args, run_full):
    """ Runs experiments to reproduce
    results of figure 1 in original ABC HotNets 2017 paper.
    """

    # For all of these experiments, we use a fixed
    # 48 Mbps downlink, and an mm-delay of 50 ms.

    delay = 50
    bw = 48
    downlink_ext = STATIC_BW_VARIABLE
    downlink_trace = os.path.join(BW_TRACE_DIR, downlink_ext)

    for scheme in schemes:
        print(" ---- Running Figure 1 Experiment for protocol: %s ---\n" % scheme)

        for trace in traces:

            uplink_trace = os.path.join(TRACE_DIR, trace)
            if args.tiny_trace:
                uplink_trace += "-tiny"

            print("   --> Running trace: %s\n" % uplink_trace)
            protocol = get_protocol(scheme, trace, downlink_ext, figure="figure1")
            cmds = protocol.get_figure1_cmds(delay, uplink_trace, downlink_trace, args)

            if (scheme, trace) in run_full:
                make_bw_file(uplink_trace, downlink_trace, bw)
                run_cmds(cmds, args.verbose)
            else:
                print(" experiment skipped: (%s, %s)" % (scheme, trace))

            time.sleep(2)

            uplink_trace_name = os.path.basename(uplink_trace)
            downlink_trace_name = os.path.basename(downlink_trace)

            retrieve_and_print_stats(
                    protocol, 2 * delay, uplink_trace_name, downlink_trace_name
            )
        time.sleep(2)


def run_fig2_exp(schemes, args, run_full):
    """ Runs experiments for the given schemes, in
    the style of figure 2.

    Runs full experiments for everything in run_full,
    assuming that results files already exist for protocols present
    in schemes but not in run_full.
    """
    delay = 50
    exp = args.experiment

    # Set up uplink/downlink trace combination

    if exp == 'figure2a':
        uplink_ext = 'Verizon-LTE-short.up'
        downlink_ext = STATIC_BW_FIXED
        uplink_trace = os.path.join(TRACE_DIR, uplink_ext)
        downlink_trace = os.path.join(BW_TRACE_DIR, downlink_ext)
    elif exp == 'figure2b':
        uplink_ext = 'Verizon-LTE-short.down'
        downlink_ext = STATIC_BW_FIXED
        uplink_trace = os.path.join(TRACE_DIR, uplink_ext)
        downlink_trace = os.path.join(BW_TRACE_DIR, downlink_ext)
    elif exp == 'bothlinks':
        uplink_ext = 'Verizon-LTE-short.up'
        downlink_ext = 'Verizon-LTE-short.down'
        uplink_trace = os.path.join(TRACE_DIR, uplink_ext)
        downlink_trace = os.path.join(TRACE_DIR, downlink_ext)
    elif exp == 'pa1':
        delay = 20
        uplink_ext = 'Verizon-LTE-short.down'
        downlink_ext = 'Verizon-LTE-short.up'
        uplink_trace = os.path.join(TRACE_DIR, uplink_ext)
        downlink_trace = os.path.join(TRACE_DIR, downlink_ext)
    else:
        raise ValueError("Unknown experiment: %s" % exp)

    if args.tiny_trace:
        uplink_trace += "-tiny"
        downlink_trace += "-tiny"

    num_runs = 1
    if args.num_runs:
        num_runs = args.num_runs

    # Run experiment for each scheme
    for scheme in schemes:
        print(" ---- Running Experiment %s for protocol: %s ---- \n" % (exp, scheme))
        protocol = get_protocol(scheme, uplink_ext, downlink_ext, exp)
        results_path, results_file = os.path.split(protocol.results_file_path)
        log_path, log_file = os.path.split(protocol.uplink_log_file_path)

        results_path_fmt = results_path + '/multiple/%d/' + results_file
        log_path_fmt = log_path + '/multiple/%d/' + log_file

        for i in range(1, num_runs + 1):
            print("         -> Iteration: %d\n" % i)

            if num_runs > 1:
                curr_results_file = results_path_fmt % i
                curr_log_file = log_path_fmt % i

                curr_log_path, _ = os.path.split(curr_log_file)
                curr_results_path, _ = os.path.split(curr_results_file)

                if not os.path.exists(curr_log_path): os.makedirs(curr_log_path)
                if not os.path.exists(curr_results_path): os.makedirs(curr_results_path)

                protocol.results_file_path = curr_results_file
                protocol.uplink_log_file_path = curr_log_file

            cmds = protocol.get_figure2_cmds(delay, uplink_trace, downlink_trace, args)
            if scheme in run_full:
                run_cmds(cmds, args.verbose)
            else:
                print(" Experiment skipped ")

            uplink_trace_name = os.path.basename(uplink_trace)
            downlink_trace_name = os.path.basename(downlink_trace)
            retrieve_and_print_stats(protocol, delay * 2, uplink_trace_name, downlink_trace_name)
            time.sleep(2)

    print(" ---- Done ---- \n")

def fig2_get_run_full(args, schemes):
    """Given a list of schemes, returns
    a list of schemes to be run in full for figure2.
    """
    run_full = schemes
    if args.reuse_results:
        if args.reuse_results == ['all']:
            run_full = []
        else:
            run_full = [s for s in schemes if s not in args.reuse_results]
    elif args.run_full:
        if args.run_full == ['all']:
            run_full = schemes
        else:
            run_full = [s for s in schemes if s not in args.run_full]
    return run_full

def fig1_get_run_full(args, schemes, traces):
    """Given a list of schemes and traces, returns
    a list of scheme/trace pairs to be run in full.
    """
    reuse_results = args.reuse_results_fig1
    if reuse_results:
        if reuse_results == ['all']:
            run_full = []
        else:
            pairs_to_skip = []
            for reuse in reuse_results:
                scheme, trace = [s.strip() for s in reuse.split(':')]
                if scheme == 'all':
                    for s in schemes:
                        pairs_to_skip.append((s, trace))
                elif trace == 'all':
                    for t in traces:
                        pairs_to_skip.append((scheme, t))
                else:
                    pairs_to_skip.append((scheme, trace))

            run_full = [(s, t) for s in schemes for t in traces \
                                    if (s, t) not in pairs_to_skip]
    else:
        run_full = [(s, t) for s in schemes for t in traces]

    return run_full

# Contains all schemes used in the ABC paper, not
# including LEDBAT, Copa, or PCC from the congestion control
# pantheon.
ALL_SCHEMES = ['abc', 'cubic', 'sprout', 'verus', 'vegas', \
        'cubiccodel', 'cubicpie', 'bbr']

# All cellular traces used in figure1.
ALL_FIG1_TRACES = [
        'Verizon-LTE-short.up',\
        'Verizon-LTE-driving.up', \
        'TMobile-LTE-driving.up', \
        'ATT-LTE-driving.up', \
        'Verizon-LTE-short.down', \
        'Verizon-LTE-driving.down', \
        'TMobile-LTE-driving.down', \
        'ATT-LTE-driving.down'
]

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--schemes', default=None, nargs='+',
        help='list of protocols to run from scratch; runs all if empty')
    parser.add_argument('--experiment', default="figure2a", type=str,
        help='The experiment to run: e.g. figure1, figure2a, figure2b, bothlinks')
    parser.add_argument('--csv-out', default=None, type=str,
        help='save results to CSV file with this name')

    parser.add_argument('--print-graph', action='store_true',
            help='print throughput graph for each protocol')
    parser.add_argument('--tiny-trace', action='store_true',
            help='use a 5 second version of the Verizon/BW traces')
    parser.add_argument('--num-runs', default=None, type=int,
            help='(fig 2) run each experiment multiple times')

    parser.add_argument('--verbose', action='store_true',
            help='be verbose during the experiment')

    skip = parser.add_mutually_exclusive_group(required=False)
    skip.add_argument('--run-full', default=None,
            help='perform a full run for the specified protocols',
            nargs='+')
    skip.add_argument('--reuse-results', default=None,
            help='(fig 2) reuse existing results for the specified protocols', nargs='+')

    # Figure 1 args
    parser.add_argument('--traces', default=None, nargs='+',
            help='(Fig 1) list of traces to run for figure 1; runs all if given \'all\' or empty')
    parser.add_argument('--reuse-results-fig1', default=None, nargs='+',
            help='(Fig 1) list of <protocol>:<trace> pairs to reuse existing results for: \
                    can give \'all\' to reuse everything specified, or <protocol>:all, all:<trace>')

    args = parser.parse_args()

    if not os.path.exists('logs'): os.makedirs('logs')
    if not os.path.exists('results'): os.makedirs('results')
    if not os.path.exists('graphs'): os.makedirs('graphs')

    # What schemes to run?
    if args.schemes:
        schemes = args.schemes
    else:
        schemes = ALL_SCHEMES

    # What traces to use? (fig1)
    if args.traces:
        traces = args.traces
    else:
        traces = ALL_FIG1_TRACES

    # What schemes to run in full and which to reuse results from?

    if args.experiment == "figure2a" or args.experiment == "figure2b" \
            or args.experiment == "bothlinks" or args.experiment == "pa1":
        run_full = fig2_get_run_full(args, schemes)
        run_fig2_exp(schemes, args, run_full)
    elif args.experiment == "figure1":
        run_full = fig1_get_run_full(args, schemes, traces)
        run_fig1_exp(schemes, traces, args, run_full)
    else:
        raise NotImplementedError("Unknown experiment: %s" % args.experiment)

    if args.num_runs and args.csv_out:
        raise ValueError("You must run the gather_multiple_results.py script to generate \
                a CSV file when you run experiments multiple times.\n")

    # Output CSV file with results, if filename passed in arguments.
    if args.csv_out:

        if not args.csv_out.endswith('.csv'):
            args.filename = '{}.csv'.format(args.csv_out)

        with open(args.csv_out, 'w') as f:
            for stats_bundle in stats:
                for proto, s in stats_bundle.items():
                    f.write('{}, {}, {}, {}, {}, {}, {}, {}, {}\n'.format(
                            proto, s.util, s.delay, s.throughput,
                            s.power, s.queuing_delay, s.per_packet_delay,
                            s.uplink_trace, s.downlink_trace
                        )
                    )
