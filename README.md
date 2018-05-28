# Intro

This repository contains logic for reproducing results from the
ABC congestion control research paper by Goyal et al.

Logic for ABC is in the file - mahimahi/src/packet/cellular_packet_queue.cc

-----

# Setup

1. Clone the repo: `https://github.com/sktollman/ABC-1.git`.
2. Create a Python 2 virtual environment within `ABC-1` and activate it.
3.  Run the setup script `sh setup/setup.sh`

The setup script will install dependencies (e.g. pip packages,  debian packages, the Stanford Pantheon for congestion control), install mahimahi, and prepare your Kernel for running experiments.

# Installing Congestion Control Modules

We need `cubic`, `vegas`, and `bbr`.
If you are running on a Google Cloud Compute instance, this part is already
taken care for you if you followed the steps in the previous section.


##### If you are not running on GCC

To see which modules are loaded in your kernel, run:
```
$ /sbin/sysctl net.ipv4.tcp_available_congestion_control
```
To see which can be run without root permissions, run:
```
$ /sbin/sysctl net.ipv4.tcp_allowed_congestion_control
```
To see the available modules, run
```
$ ls -la /lib/modules/$(uname -r)/kernel/net/ipv4
```
To load modules, run `modprobe`. (eg: `sudo modprobe -a tcp_vegas`). You should now see these modules in the list of available congestion control protocols. You may still need to enable some to run without root permissions. In this case, you will need to append to that file. When writing to the file you want to make sure that you don't remove existing protocols. (e.g. `$ echo cubic reno bbr vegas | sudo tee /proc/sys/net/ipv4/tcp_allowed_congestion_control`)

# Reproduction

## Figure 2

`experiments.py` contains the code to reproduce Figure 2 (as well as other figures). This runs traces against each protocol and optionally saves the utilization and delay results to a csv file. The `--schemes` command-line parameter takes in a comma-separated list of protocols to run.  If the option is not given, results for all protocols are generated. The `--experiment` parameter takes a string in `figure2a, figure2b, bothlinks` according to which experiment we are running.

For example, to generate ABC and Verus results for Figure 2a, run `python experiment.py --experiment figure2a --schemes abc verus`.

The `--reuse-results` and `--run-full` parameters allow the developer to specify exactly which experiments to re-run, and which to only display results from given that a results file exists.  For example, `python experiment.py --experiment figure2a --schemes abc sprout --reuse-results abc` will return Figure 2a results for ABC and Sprout, but will only fully re-run the experiment for Sprout, because ABC is skipped.  Not specifying any of these commands will spur a fresh run of all the protocols given in `--schemes`.

Lastly, the command-line parameter `--csv-out` allows you to specify a filename to which experiment results will be printed in csv format.  This file is consumed by the plotting scripts described in the next section.

### Generating Figure Plots

`figure2_plot.py` takes a csv results file from `experiments.py` and creates a matplotlib graph with the same format as the figure from the original paper. These two scripts are separate because I [Sarah] could not get matplotlib running on the virtual machine I am using for mahimahi, so I am creating the csv on the machine and the graph on my local machine.

Example:
```
$ python figure2.py --uplink --filename results
$ python figure2_plot.py --data_filename results.csv --plot-filename plot
```
