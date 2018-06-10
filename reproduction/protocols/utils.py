#
# Contains utility routines for our reproduction.
#

import os
from protocols.cc_protocol import CCProtocol

UPLINK_LOG_FILE_FMT = 'logs/{}/{}/UPLINK_{}-DOWNLINK_{}.log'
RESULTS_FILE_FMT = 'results/{}/{}/UPLINK_{}-DOWNLINK_{}.txt'
CONFIG_FILE_FMT = '~/ABC-1/reproduction/protocols/config/{}.json'

def get_protocol(scheme, uplink_ext, downlink_ext, figure="figure2"):
    """Returns a CCProtocol object populated with
       the correct scheme arguments, ready to extract
       figure commands from.

    Args:
        scheme: (str) what scheme to return CCProtocol for
        uplink_ext: (str) the name of the uplink trace file
        downlink_ext: (str) the name of the downlink trace file

    """

    results_file_path = RESULTS_FILE_FMT.format(
            figure, scheme, uplink_ext, downlink_ext
    )
    uplink_log_file_path = UPLINK_LOG_FILE_FMT.format(
            figure, scheme, uplink_ext, downlink_ext
    )

    results_dir = os.path.dirname(results_file_path)
    log_dir = os.path.dirname(uplink_log_file_path)

    if not os.path.exists(results_dir): os.makedirs(results_dir)
    if not os.path.exists(log_dir): os.makedirs(log_dir)

    extra_config = {}
    
    config_file_name = None

    if scheme in ['copa', 'ledbat', 'pcc', 'quic', 'verus', 'cubic', 'abc', 'sprout']:
        config_file_name = scheme
    
    elif scheme == 'vegas': 
        config_file_name = 'cubic'
        extra_config['name'] = 'vegas'
        extra_config['mahimahi_command'] = 'sh ~/ABC-1/start_tcp.sh vegas'

    elif scheme == 'cubiccodel': 
        config_file_name = 'cubic'
        extra_config['name'] = 'cubiccodel'
        extra_config['uplink_queue'] = 'codel'
        extra_config['uplink_queue_args'] = 'packets=100,target=50,interval=100'

    elif scheme == 'cubicpie':
        config_file_name = 'cubic'
        extra_config['name'] = 'cubicpie'
        extra_config['uplink_queue'] = 'pie'
        extra_config['uplink_queue_args'] = 'packets=100,qdelay_ref=50,max_burst=100'

    elif scheme == 'bbr':
        config_file_name = 'cubic'
        extra_config['name'] = 'bbr'
        extra_config['mahimahi_command'] = 'sh ~/ABC-1/start_tcp.sh bbr'

    else:
        raise ValueError("Unknown scheme: %s" % scheme)
    
    config_file_path = CONFIG_FILE_FMT.format(config_file_name)

    p = CCProtocol(config_file_path, results_file_path, uplink_log_file_path, extra_config)
    return p


