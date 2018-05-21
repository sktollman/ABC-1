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

Run `$ /sbin/sysctl net.ipv4.tcp_available_congestion_control` to see which modules are loaded in your kernel, and `$ /sbin/sysctl net.ipv4.tcp_allowed_congestion_control` to see which can be run without root permissions. We need `cubic`, `vegas`, and `bbr`.

Run `$ ls -la /lib/modules/$(uname -r)/kernel/net/ipv4` to see the available modules.

Run `modprobe` to load the modules that you need. For example:
```
$ sudo modprobe -a tcp_vegas
$ sudo modprobe -a tcp_bbr
```

Running `$ /sbin/sysctl net.ipv4.tcp_available_congestion_control` again should now contain these modules.
Some may still be missing from `$ /sbin/sysctl net.ipv4.tcp_allowed_congestion_control`. In this case, you will need to append to that file. When writing to the file you want to make sure that you don't remove existing protocols. For example:
```
echo cubic reno bbr vegas | sudo tee /proc/sys/net/ipv4/tcp_allowed_congestion_control
```

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
