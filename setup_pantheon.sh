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
sh fetch_submodules.sh
test/setup.py --install-deps --schemes "sprout verus"
git add .

# Make sure we catch the sysctl binary if it is in /sbin
export PATH=$PATH:/sbin

test/setup.py --schemes "sprout verus"
cd ~/ABC-1
