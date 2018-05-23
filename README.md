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

# Installing Congestion Control Modules

We need `cubic`, `vegas`, and `bbr`.
If you are running on a Google Cloud Compute instance, you can run:
```
$ sh install_kernal_cc.sh
```
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

### Figure 2a

`figure2.py` contains the code to reproduce Figure 2a or b. This runs traces against each protocol and optionally saves the utilization and delay results to a csv file. The `--skip` and `--skip-all-except` parameters allow the developer to reuse previous results for a given protocol to save time. For Figure 2a, use the `--uplink` parameter. For Figure 2b, use the `--downlink` parameter. To run an experiment that uses a varying downlink, use the `--bothlinks` parameter.

`figure2_plot.py` takes a results file from `figure2.py` and creates a matplotlib graph with the same format as the figure from the original paper. These two scripts are separate because I [Sarah] could not get matplotlib running on the virtual machine I am using for mahimahi, so I am creating the csv on the machine and the graph on my local machine.

Example:
```
$ python figure2.py --uplink --filename results
$ python figure2_plot.py --data_filename results.csv --plot-filename plot
```
