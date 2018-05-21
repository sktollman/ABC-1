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
cd mahimahi && ./autogen.sh && ./configure && make && sudo make install

# Make sure we have congestion control Pantheon
cd ~
if [ ! -d "./pantheon"]; then
  git clone https://github.com/StanfordSNR/pantheon.git
fi
cd ~/ABC-1

# Setup Pantheon
sh setup/setup_pantheon.sh 