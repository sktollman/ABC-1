#!/usr/bin/python

#
# Runs experiments to generate the figures in our
# ABC reproduction.
#

from subprocess import call
from collections import namedtuple
from protocols.cc_protocol import CCProtocol
from utils import get_protocol

import os
import argparse

TRACE_DIR = '~/ABC-1/mahimahi/traces/'
BW_TRACE_DIR = '~/ABC-1'

STATIC_BW = 'bw48.mahi'

UPLINK_LOG_FILE_FMT = 'logs/{}-UPLINK_{}-DOWNLINK_{}.log'
RESULTS_FILE_FMT = 'results/{}-UPLINK_{}-DOWNLINK_{}.txt'

Stats = namedtuple('Stats', ['util', 'delay', 'throughput', 'power', 'queuing_delay'])
stats = dict()

def print_fig2_results(cc_proto):
    """ Prints results for a figure 2 - type experiment.

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
            power_score = 1000 * avg_throughput / float(signal_delay)

            stats[proto_name] = Stats(utilization, signal_delay, avg_throughput, power_score, queuing_delay)

            print("\n  ~~ Results for protocol: %s ~~" % proto_name)
            print("\tutilization: %s%%" % str(round(100 * utilization, 2)))
            print("\tthroughput: %s" % str(avg_throughput))
            print("\tsignal delay: %s" % str(signal_delay))
            print("\tqueuing delay: %s" % str(queuing_delay))
            print("\tpower score: %s\n" % str(power_score))

    else:
        print("No results found for proto %s at path: %s" 
                % (proto_name, cc_proto.results_file_path))

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
        downlink_ext = STATIC_BW
        uplink_trace = os.path.join(TRACE_DIR, uplink_ext)
        downlink_trace = os.path.join(BW_TRACE_DIR, downlink_ext)
    elif exp == 'figure2b':
        uplink_ext = STATIC_BW
        downlink_ext = 'Verizon-LTE-short.down'
        uplink_trace = os.path.join(BW_TRACE_DIR, uplink_ext)
        downlink_trace = os.path.join(TRACE_DIR, downlink_ext)
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
 
    # Run each scheme experiment
    
    for scheme in schemes:
        print(" ---- Running Experiment %s for protocol: %s ---- \n" % (exp, scheme))
        protocol = get_protocol(scheme, uplink_ext, downlink_ext)
        cmds = protocol.get_figure2_cmds(delay, uplink_trace, downlink_trace, args)
        
        
        if scheme in run_full:
            for c in cmds:
                print("$ %s" % ' '.join(c.split(' ')))
                call(c, shell=True)
        else:
            print(" Experiment skipped ")

        print_fig2_results(protocol)
        print(" ---- Done ---- \n")

ALL_SCHEMES = ['abc', 'cubic', 'sprout', 'verus', 'vegas', \
        'cubiccodel', 'cubicpie', 'bbr']

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--schemes', default=None, nargs='+',
        help='list of protocols to run from scratch; runs all if empty')
    parser.add_argument('--experiment', default="figure2a", type=str,
        help='The experiment to run: e.g. figure2a, figure2b, bothlinks')
    parser.add_argument('--csv-out', default=None, type=str,
        help='save results to CSV file with this name')

    parser.add_argument('--print-graph', action='store_true',
            help='print throughput graph for each protocol')

    skip = parser.add_mutually_exclusive_group(required=False)
    skip.add_argument('--run-full', default=None,
            help='perform a full run for the specified protocols',
            nargs='+')
    skip.add_argument('--reuse-results', default=None,
            help='reuse existing results for the specified protocols', nargs='+')
    
    args = parser.parse_args()
    
    if not os.path.exists('logs'): os.makedirs('logs')
    if not os.path.exists('results'): os.makedirs('results')
    
    # What schemes to run?
    if args.schemes:
        schemes = args.schemes
    else:
        schemes = ALL_SCHEMES
    
    # What schemes to run in full and which to reuse results from?
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
    
    if args.experiment == "figure2a" or args.experiment == "figure2b" \
            or args.experiment == "bothlinks" or args.experiment == "pa1":
        run_fig2_exp(schemes, args, run_full)
    else:
        raise NotImplementedError("Unknown experiment: %s" % args.experiment)
    
    # Output CSV file with results, if filename passed in arguments.
    if args.csv_out:

        if not args.csv_out.endswith('.csv'):
            args.filename = '{}.csv'.format(args.csv_out)
        
        with open(args.csv_out, 'w') as f:
            for proto, s in stats.items():
                f.write('{}, {}, {}, {}, {}, {}\n'.format(proto, 
                    s.util, s.delay, s.throughput, s.power, s.queuing_delay))
