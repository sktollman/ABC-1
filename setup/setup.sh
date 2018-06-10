#
# Script to set up experiment environment.
#
#   Should only need to be run once,
#   ideally inside a virtual env.
#

# Install requirements
pip install -r ~/ABC-1/requirements.txt

# Setup mahimahi dependencies
sh setup/install_mahimahi_deps.sh

# Setup mahimahi
cd mahimahi && sh autogen.sh && sh configure && make && sudo make install

# Make sure we have congestion control Pantheon
cd ~
if [ ! -d "pantheon" ]; then
  git clone https://github.com/StanfordSNR/pantheon.git
fi
cd ~/ABC-1

# Setup congestion control schmees
sh install_kernel_cc.sh

# Make start-tcp executable
chmod +x start_tcp.sh

# Make a full length 140-second 48 Mbps mahi file
python make_mahi_trace.py --length 140000 -bw 48 > bw48.mahi

# Setup Pantheon
sh setup/setup_pantheon.sh
