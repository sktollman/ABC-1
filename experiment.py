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

Stats = namedtuple('Stats', ['util', 'delay', 'throughput', 'power'])
stats = dict()

def print_fig2_results(cc_proto):
    """ Prints results for a figure 2 experiment. 
    """

    proto_name = cc_proto.config['name']

    if os.path.isfile(cc_proto.results_file_path):
        with open(cc_proto.results_file_path) as f:
            lines = f.readlines()
            avg_capacity = float(lines[0].split(' ')[2])
            avg_throughput = float(lines[1].split(' ')[2])
            queueing_delay = float(lines[2].split(' ')[5])
            signal_delay = float(lines[3].split(' ')[4])

            utilization = avg_throughput / avg_capacity
            power_score = 1000 * avg_throughput / float(signal_delay)

            stats[proto_name] = Stats(utilization, signal_delay, avg_throughput, power_score)

            print("\n  ~~ Results for protocol: %s ~~" % proto_name)
            print("\tutilization: %s" % str(round(100 * utilization, 2)))
            print("\tthroughput: %s" % str(avg_throughput))
            print("\tdelay: %s" % str(signal_delay))
            print("\tpower score: %s\n" % str(power_score))

    else:
        print("No results found for proto %s at path: %s" 
                % (proto_name, cc_proto.results_file_path))

def run_fig2(schemes, fig):
    """ Runs Figure 2 experiments for the given schemes. 
    """
    delay = 20
    
    # Set up uplink/downlink trace combination
    
    if fig == '2a':
        uplink_ext = 'Verizon-LTE-short.up'
        downlink_ext = STATIC_BW
        uplink_trace = os.path.join(TRACE_DIR, uplink_ext)
        downlink_trace = os.path.join(BW_TRACE_DIR, downlink_ext)
    elif fig == '2b':
        uplink_ext = STATIC_BW
        downlink_ext = 'Verizon-LTE-short.down'
        uplink_trace = os.path.join(BW_TRACE_DIR, uplink_ext)
        downlink_trace = os.path.join(TRACE_DIR, downlink_ext)
    elif fig == '2c':
        # TODO: need to figure this one out
        raise NotImplementedError
    else:
        raise ValueError("Unknown figure: %s" % fig)
 
    # Run each scheme experiment
    
    for scheme in schemes:
        print(" ---- Running Figure 2a exp for protocol: %s ---- " % scheme)
        protocol = get_protocol(scheme, uplink_ext, downlink_ext)
        cmds = protocol.get_figure2_cmds(delay, uplink_trace, downlink_trace)
        
        for c in cmds:
            print("$ %s" % c)
            call(c, shell=True)

        print_fig2_results(protocol)
        print(" ---- Done ---- \n")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--schemes', default=None, type=str,
        help='comma-separated list of protocols to run from scratch; runs all if empty')
    parser.add_argument('--figure', default="2a", type=str,
        help='The figure to run an experiment for: 1, 2a, 2b, 2c, 4')
    parser.add_argument('--csv_out', default=None, type=str,
        help='save results to CSV file with this name')
    
    args = parser.parse_args()
    
    if not os.path.exists('logs'): os.makedirs('logs')
    if not os.path.exists('results'): os.makedirs('results')

    if args.schemes:
        schemes = args.schemes.split(',')
    
    if args.figure == '1':
        raise NotImplementedError
    elif args.figure == '2a' or args.figure == '2b' or args.figure == '2c':
        run_fig2(schemes, args.figure)
    elif args.figure == '4':
        raise NotImplementedError
    else:
        raise ValueError("Unknown figure: %s" % args.figure)
    
    # Output CSV file with results, if filename passed in arguments.
    if args.csv_out:

        if not args.csv_out.endswith('.csv'):
            args.filename = '{}.csv'.format(args.csv_out)
        
        with open(args.csv_out, 'w') as f:
            for proto, s in stats.items():
                f.write('{}, {}, {}, {}, {}\n'.format(proto, s.util, s.delay))
