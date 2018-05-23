#!/usr/bin/python

import os
import argparse

from subprocess import call
from collections import namedtuple

TRACE_DIR = '~/ABC-1/mahimahi/traces/'
UPLINK_EXT = 'Verizon-LTE-short.up'
DOWNLINK_EXT = 'Verizon-LTE-short.down'
STATIC_BW = '~/ABC-1/bw48.mahi'
DELAY = 50

Protocol = namedtuple('Protocol', ['name', 'pre_commands', 'post_commands',
    'uplink_queue', 'uplink_queue_args', 'commands'])
Stats = namedtuple('Stats', ['util', 'delay'])

ABC = Protocol(
    name='abc',
    pre_commands=['python server.py &'],
    post_commands=['pkill -f server.py'],
    uplink_queue='cellular',
    uplink_queue_args='packets=100,qdelay_ref=50,beta=75',
    commands='python client.py'
)

CUBIC = Protocol(
    name='cubic',
    pre_commands=['iperf -s -p 42425 -w 16m &'],
    post_commands=['killall iperf'],
    uplink_queue='droptail',
    uplink_queue_args='packets=100',
    commands='./start-tcp.sh cubic'
)

SPROUT = Protocol(
    name='sprout',
    pre_commands=["python ~/pantheon/src/wrappers/sprout.py receiver 12345 &"],
    post_commands=["sleep 140; pkill -f sproutbt2"],
    uplink_queue='droptail',
    uplink_queue_args='packets=100',
    commands='python ~/pantheon/src/wrappers/sprout.py sender 100.64.0.1 12345 &'
)

VERUS = Protocol(
    name='verus',
    pre_commands=["python ~/pantheon/src/wrappers/verus.py sender 12312 &; sleep 10"],
    post_commands=["sleep 75; pkill -f verus_client; pkill -f verus_server"],
    uplink_queue='droptail',
    uplink_queue_args='packets=100',
    commands='python ~/pantheon/src/wrappers/verus.py receiver 100.64.0.1 12312 &'
)

# TODO: fix vegas!
# Attempt to set 'vegas' congestion control failed: No such file or directory
VEGAS = CUBIC._replace(
    name='vegas',
    commands='./start-tcp.sh vegas'
)
CUBIC_CODEL = CUBIC._replace(
    name='cubiccodel',
    uplink_queue='codel',
    uplink_queue_args='packets=100,target=50,interval=100'
)
CUBIC_PIE = CUBIC._replace(
    name='cubicpie',
    uplink_queue='pie',
    uplink_queue_args='packets=100,qdelay_ref=50,max_burst=100'
)
BBR = CUBIC._replace(
    name='bbr',
    commands='./start-tcp.sh bbr'
)

PANTHEON_PROTOS = [SPROUT, VERUS]
PROTOS = [BBR, VEGAS, ABC, CUBIC, CUBIC_CODEL, CUBIC_PIE, SPROUT, VERUS]
stats = dict()

def run_exp(proto, uplink_ext, downlink, skip=False):
    uplink = '{}{}'.format(TRACE_DIR, uplink_ext)
    uplink_log_file = 'logs/{}-{}.log'.format(uplink_ext, proto.name)
    results_file = 'results/{}-{}.txt'.format(uplink_ext, proto.name)

    if not skip:
        print('Running {} experiment...'.format(proto.name))

        exp = 'mm-delay {delay} mm-link --uplink-log={uplink_log} \
            --uplink-queue={uplink_queue} --uplink-queue-args=\"{uplink_queue_args}\" \
            {uplink} {downlink} {commands}'.format(delay=DELAY, uplink_log=uplink_log_file,
                uplink_queue=proto.uplink_queue, uplink_queue_args=proto.uplink_queue_args,
                uplink=uplink, downlink=downlink, commands=proto.commands)
        results = 'mm-throughput-graph 500 {log_file} > /dev/null 2> {results_file}'.format(
            log_file=uplink_log_file, results_file=results_file)

        commands = list(proto.pre_commands[0].split(';'))
        commands.append(exp)
        commands.extend(proto.post_commands[0].split(';'))
        commands.append(results)
        for c in commands:
            print("$ %s" % c)
            call(c, shell=True)

    if os.path.isfile(results_file):
        with open(results_file) as f:
            lines = f.readlines()
            avg_capacity = float(lines[0].split(' ')[2])
            avg_throughput = float(lines[1].split(' ')[2])
            queueing_delay = float(lines[2].split(' ')[5])
            signal_delay = float(lines[3].split(' ')[4])

            utilization = avg_throughput / avg_capacity

            stats[proto.name] = Stats(utilization, signal_delay)

            print('{} results: utilization={}%, delay={}ms'.format(proto.name,
                round(100 * utilization, 2), signal_delay))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    skip = parser.add_mutually_exclusive_group(required=False)
    skip.add_argument('--skip-all-except', default=None,
        help='only perform a fresh run for the specified protocols', nargs='*')
    skip.add_argument('--skip', default=None,
        help='skip the specified protocols', nargs='+')
    parser.add_argument('--filename', default=None,
        help='save the results to a csv with this name', type=str)
    parser.add_argument('--scheme', default=None, type=str,
        help='only run this scheme end to end')

    links = parser.add_mutually_exclusive_group(required=True)
    links.add_argument('--uplink', action='store_true', default=False)
    links.add_argument('--downlink', action='store_true', default=False)
    links.add_argument('--bothlinks', action='store_true', default=False)
    args = parser.parse_args()

    run_protos = list(PROTOS)
    if args.skip:
        run_protos = filter(lambda p: p.name not in args.skip, run_protos)
    elif args.skip_all_except:
        run_protos = filter(lambda p: p.name in args.skip_all_except, run_protos)
    
    # these two directories are required
    if not os.path.exists('logs'): os.makedirs('logs')
    if not os.path.exists('results'): os.makedirs('results')

    uplink_ext = UPLINK_EXT if args.uplink or args.bothlinks else DOWNLINK_EXT
    downlink = STATIC_BW if not args.bothlinks else '{}{}'.format(TRACE_DIR, DOWNLINK_EXT)
    for p in PROTOS:
        if args.scheme and p.name != args.scheme:
            continue
        run_exp(p, uplink_ext, downlink, not p in run_protos)

    if args.filename:
        if not args.filename.endswith('.csv'):
            args.filename = '{}.csv'.format(args.filename)
        # overwrite file if exists
        with open(args.filename, 'w') as f:
            for proto, s in stats.items():
                f.write('{}, {}, {}\n'.format(proto, s.util, s.delay))
