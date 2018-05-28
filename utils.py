#
# Contains utility routines for our reproduction.
#

from protocols.cc_protocol import CCProtocol

UPLINK_LOG_FILE_FMT = 'logs/{}-UPLINK_{}-DOWNLINK_{}.log'
RESULTS_FILE_FMT = 'results/{}-UPLINK_{}-DOWNLINK_{}.txt'

def get_protocol(scheme, uplink_ext, downlink_ext):
    """Returns a CCProtocol object populated with
       the correct scheme arguments, ready to extract
       figure commands from. 

    Args:
        scheme: (str) what scheme to return CCProtocol for
        uplink_ext: (str) the name of the uplink trace file
        downlink_ext: (str) the name of the downlink trace file

    """
    
    config_file_path = None
    results_file_path = RESULTS_FILE_FMT.format(scheme, uplink_ext, downlink_ext)
    uplink_log_file_path = UPLINK_LOG_FILE_FMT.format(scheme, uplink_ext, downlink_ext)

    extra_config = {}
    
    if scheme == "abc":
        config_file_path = 'protocols/config/abc.json'

    elif scheme == "cubic":
        config_file_path = 'protocols/config/cubic.json'

    elif scheme == "sprout":
        config_file_path = 'protocols/config/sprout.json'

    elif scheme == "verus":
        config_file_path = 'protocols/config/verus.json'

    elif scheme == "vegas":
        config_file_path = 'protocols/config/cubic.json'
        extra_config['name'] = 'vegas'
        extra_config['mahimahi_command'] = './start-tcp.sh vegas'

    elif scheme == "cubiccodel":
        config_file_path = 'protocols/config/cubic.json'
        extra_config['name'] = 'cubiccodel'
        extra_config['uplink_queue'] = 'codel'
        extra_config['uplink_queue_args'] = 'packets=100,target=50,interval=100'

    elif scheme == "cubicpie":
        config_file_path = 'protocols/config/cubic.json'
        extra_config['name'] = 'cubicpie'
        extra_config['uplink_queue'] = 'pie'
        extra_config['uplink_queue_args'] = 'packets=100,qdelay_ref=50,max_burst=100'

    elif scheme == "bbr":
        config_file_path = 'protocols/config/cubic.json'
        extra_config['name'] = 'bbr'
        extra_config['mahimahi_command'] = './start-tcp.sh bbr'

    elif scheme == "copa":
        config_file_path = 'protocols/config/copa.json'

    else:
        raise ValueError("Unknown scheme: %s" % scheme)

    p = CCProtocol(config_file_path, results_file_path, uplink_log_file_path, extra_config)
    return p


