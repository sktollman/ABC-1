sudo modprobe -a tcp_vegas
sudo modprobe -a tcp_bbr
echo cubic reno bbr vegas | sudo tee /proc/sys/net/ipv4/tcp_allowed_congestion_control
