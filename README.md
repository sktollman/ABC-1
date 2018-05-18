# ABC-AQM

Installing Mahimahi
```
$ cd mahimahi && ./autogen.sh && ./configure && make && sudo make install
$ sudo sysctl -w net.ipv4.ip_forward=1
```
(have to enable Linux's IP forwarding for mahimahi to work)

For any issues with mahimahi refer to - http://mahimahi.mit.edu

run-exp.sh contains example of how to run various schemes.

Logic for ABC is in the file - mahimahi/src/packet/cellular_packet_queue.cc

-----

# Reproduction

## Figure 2

### Figure 2a

`figure2.py` contains the code to reproduce Figure 2a. This runs traces against each protocol and optionally saves the utilization and delay results to a csv file. The `--skip` and `--skip-all-except` parameters allow the developer to reuse previous results for a given protocol to save time.

`figure2a_plot.py` takes a results file from `figure2.py` and creates a matplotlib graph with the same format as the figure from the original paper. These two scripts are separate because I [Sarah] could not get matplotlib running on the virtual machine I am using for mahimahi, so I am creating the csv on the machine and the graph on my local machine.

Example:
```
$ python figure2.py --filename results.csv
$ python figure2a_plot.py --filename results.csv
```
