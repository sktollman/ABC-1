#
# Script to set up experiment environment.
#   
#   Should only need to be run once,
#   ideally inside a virtual env.
#

# Install requirements
pip install -r requirements.txt

# Setup congestion control pantheon
sh setup_pantheon.sh 
