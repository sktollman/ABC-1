#
# Runs commands necessary to set up Pantheon. 
#
#    Assumes that the pantheon directory is in
#    the home directory.
#    
#    Only sets up the following congestion control
#    schemes:
#
#     - Verus
#     - Sprout
#      

cd ~/pantheon
sh tools/fetch_submodules.sh
src/experiments/setup.py --install-deps --schemes "sprout verus"

# Make sure we catch the sysctl binary if it is in /sbin
export PATH=$PATH:/sbin

sudo sysctl -w net.ipv4.ip_forward=1

src/experiments/setup.py --setup --schemes "sprout verus"
src/experiments/setup.py --schemes "sprout verus"

# Apply patches to Pantheon code
cd ~/ABC/patches
sh apply_pantheon_patches.sh

cd ~/ABC-1
