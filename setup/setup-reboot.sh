#
# Script to set up environment after reboot,
#   

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Setup congestion control schemes in the kernel
sh install_kernel_cc.sh
