#!/usr/bin/python

from subprocess import call
from collections import namedtuple

UPLINK_EXT = 'Verizon-LTE-short.up'
UPLINK = '~/ABC-1/mahimahi/traces/{}'.format(UPLINK_EXT)
DOWNLINK = '~/ABC-1/bw48.mahi'
DELAY = 50

Protocol = namedtuple('Protocol', ['name', 'pre_commands', 'post_commands',
    'uplink_queue', 'uplink_queue_args', 'commands'])
Stats = namedtuple('Stats', ['util', 'delay'])

ABC = Protocol(
    name='abc',
    pre_commands=['python server.py &'],
    post_commands=['pkill -f server.py'],
    uplink_queue='cellular',
    # TODO: make packets consistent between protocols...
    uplink_queue_args='packets=250,qdelay_ref=50,beta=75',
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
# TODO: fix BBR!
# qdisc fq 8001: root refcnt 2 limit 10000p flow_limit 100p buckets 1024 quantum 3000 initial_quantum 15000
# Attempt to set 'bbr' congestion control failed: No such file or directory
BBR = CUBIC._replace(
    name='bbr',
    commands='./start-tcp.sh bbr'
)

PROTOS = [ABC, CUBIC, CUBIC_CODEL, CUBIC_PIE]
stats = dict()

def run_exp(proto, skip=False):
    uplink_log_file = 'logs/{}-{}.log'.format(UPLINK_EXT, proto.name)
    results_file = 'results/{}-{}.txt'.format(UPLINK_EXT, proto.name)

    if not skip:
        print('Running {} experiment...'.format(proto.name))

        exp = 'mm-delay {delay} mm-link --uplink-log={uplink_log} \
            --uplink-queue={uplink_queue} --uplink-queue-args=\"{uplink_queue_args}\" \
            {uplink} {downlink} {commands}'.format(delay=DELAY, uplink_log=uplink_log_file,
                uplink_queue=proto.uplink_queue, uplink_queue_args=proto.uplink_queue_args,
                uplink=UPLINK, downlink=DOWNLINK, commands=proto.commands)
        results = 'mm-throughput-graph {delay} {log_file} > /dev/null 2> {results_file}'.format(
            delay=DELAY, log_file=uplink_log_file, results_file=results_file)

        commands = list(proto.pre_commands)
        commands.append(exp)
        commands.extend(proto.post_commands)
        commands.append(results)
        for c in commands:
            call(c, shell=True)

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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-all-except', default=None,
        help='only perform a fresh run for the specified protocols', nargs='*')
    parser.add_argument('--skip', default=None,
        help='skip the specified protocols', nargs='+')
    parser.add_argument('--filename', default=None,
        help='save the results to a csv with this name', type=str)
    args = parser.parse_args()

    not_both_params = not args.skip or not args.skip_all_except
    assert not_both_params, '--skip-all-except and --skip cannot be used concurrently'

    run_protos = list(PROTOS)
    if args.skip:
        run_protos = filter(lambda p: p.name not in args.skip, run_protos)
    elif args.skip_all_except:
        run_protos = filter(lambda p: p.name in args.skip_all_except, run_protos)

    # these two directories are required
    import os
    if not os.path.exists('logs'): os.makedirs('logs')
    if not os.path.exists('results'): os.makedirs('results')

    for p in PROTOS:
        run_exp(p, not p in run_protos)

    if args.filename:
        if not args.filename.endswith('.csv'):
            args.filename = '{}.csv'.format(args.filename)
        # overwrite file if exists
        with open(args.filename, 'w') as f:
            for proto, s in stats.items():
                f.write('{}, {}, {}\n'.format(proto, s.util, s.delay))