#!/bin/bash

# Master script that forever runs full-length
# experiments to generate results for figures 1,
# 2a, 2b, and 1 but with varying up and downlinks.
#

times_to_run_figs=5

echo "MASTER ITERATION: 1"

# 1. Generate results for figure1
python reproduction/experiment.py \
  --experiment figure1 \
  --schemes abc sprout cubicpie cubiccodel verus vegas cubic bbr copa ledbat pcc \
  --csv-out figure1.csv \

mv figure1.csv results/

# 2. Generate results for figure2a
python reproduction/experiment.py \
  --experiment figure2a \
  --schemes abc sprout cubicpie cubiccodel verus vegas cubic bbr copa ledbat pcc \
  --num-runs $times_to_run_figs \

# 3. Generate results for figure2b
python reproduction/experiment.py \
  --experiment figure2b \
  --schemes abc sprout cubicpie cubiccodel verus vegas cubic bbr copa ledbat pcc \
  --num-runs $times_to_run_figs \


# 4. Generate results for figure2 bothlinks
python reproduction/experiment.py \
  --experiment bothlinks \
  --schemes abc sprout cubicpie cubiccodel verus vegas cubic bbr copa ledbat pcc \
  --num-runs $times_to_run_figs \

# 5. Gather results for 2a, 2b, and bothlinks

python reproduction/utils/gather_multiple_results.py \
  --schemes abc sprout cubicpie cubiccodel verus vegas cubic bbr copa ledbat pcc \
  --experiment figure2a \
  --num-runs $times_to_run_figs > results/figure2a.csv

python reproduction/utils/gather_multiple_results.py \
  --schemes abc sprout cubicpie cubiccodel verus vegas cubic bbr copa ledbat pcc \
  --experiment figure2b \
  --num-runs $times_to_run_figs > results/figure2b.csv

python reproduction/utils/gather_multiple_results.py \
  --schemes abc sprout cubicpie cubiccodel verus vegas cubic bbr copa ledbat pcc \
  --experiment bothlinks \
  --num-runs $times_to_run_figs > results/bothlinks.csv


# Move the entire results/logs directory into its own one for this iteration.
mv results results-1
mkdir results

mv logs logs-1
mkdir logs
