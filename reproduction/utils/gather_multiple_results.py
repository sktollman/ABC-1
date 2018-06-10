#
# Gathers results from many experiment runs
# and prints the results to the terminal.
#
# Assumes that result files from multiple runs
# are underneath results/figure2/<proto>/multiple/<1, 2, 3 ... >/*
#
# Assumes that all protocols were run the same number of
# times.

import argparse
import os

def gather_results(schemes, num_runs, experiment):

    results_dir_fmt = 'results/%s/%s/multiple/%d/'

    delay = 50 # For essentially all experiments we do, delay is 50
    if experiment == 'pa1':
        delay = 20
    
    for scheme in schemes:
        for i in range(1, num_runs + 1):
            results_dir = results_dir_fmt % (experiment, scheme, i)
            result_files = os.listdir(results_dir)
            if len(result_files) != 1:
                raise ValueError(
                    "Found more than one results file at %s." % results_dir
                )
            results_file = os.listdir(results_dir)[0]
            results_path = os.path.join(results_dir, results_file)
            with open(results_path) as f:
                lines = f.readlines()
                avg_capacity = float(lines[0].split(' ')[2])
                avg_throughput = float(lines[1].split(' ')[2])
                queuing_delay = float(lines[2].split(' ')[5])
                signal_delay = float(lines[3].split(' ')[4])

                per_packet_delay = 2 * delay + queuing_delay
                utilization = avg_throughput / avg_capacity
                power_score = 1000 * avg_throughput / float(signal_delay)

                print("{}, {}, {}, {}, {}, {}, {}, _, _".format(
                    scheme, str(utilization), str(signal_delay), 
                    str(avg_throughput), str(power_score), str(queuing_delay), 
                    str(per_packet_delay)
                    )
                )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--schemes', default=None, nargs='+',
            help='what schemes to gather results for')

    parser.add_argument('--num-runs', default=None, type=int,
            help='number of times schemes were run')

    parser.add_argument('--experiment', default=None, type=str,
            help='what experiment to gather results for')

    args = parser.parse_args()

    if not args.schemes or not args.num_runs or not args.experiment:
        raise valueError("Must specify both --schemes and --num-runs and --experiment")

    gather_results(args.schemes, args.num_runs, args.experiment)

    

