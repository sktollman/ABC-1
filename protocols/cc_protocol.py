#
# Defines base class for a Congestion Control
# protocol used to run experiments for our 
# reproduction of the ABC paper.
#

import json
import pprint


class CCProtocol:

    fig_2_base_cmd_fmt = "mm-delay {delay} \
            mm-link --once --uplink-log={uplink_log} \
            {queue_args} \
            {uplink} {downlink} \
            {mahimahi_command}"

    fig_2_results_cmd_fmt = "mm-throughput-graph 500 {log_file} > \
            /dev/null 2> {results_file}"

    mahimahi_queue_args_fmt = "--uplink-queue={uplink_queue} \
            --uplink-queue-args=\"{uplink_queue_args}\""

    def __init__(self, config_file_path, results_file_path, 
            uplink_log_file_path, extra_args):
        """Constructs class representing a testable protocol. 

        This class houses the configuration for a congestion
        control protocol and returns commands to run to generate
        various figures in our reproduction of ABC.
        
        Reads a configuration dict from the specified JSON file. 
        Any arguments in extra_args are added to the protocol's 
        config dictionary, overwriting defaults from the JSON file.
        """
        with open(config_file_path) as f:
            self.config = json.load(f)
        
        self.results_file_path = results_file_path
        self.uplink_log_file_path = uplink_log_file_path

        for arg in extra_args:
            self.config[arg] = extra_args[arg]

    def get_figure1_cmds(self):
        """ Returns list of commands to run to generate Figure 1 results.
        """
        raise NotImplementedError

    def get_figure2_cmds(self, mm_delay, uplink_trace, downlink_trace):
        """ Returns list of commands to run to generate Figure 2 results.
        """
        
        queue_args = self.mahimahi_queue_args_fmt.format(uplink_queue=self.config['uplink_queue'],
                                        uplink_queue_args=self.config['uplink_queue_args'])

        prep_commands = self.config['prep_commands']
        mahimahi_cmd = self.fig_2_base_cmd_fmt.format(delay=str(mm_delay),
                                                 uplink_log=self.uplink_log_file_path,
                                                 queue_args=queue_args,
                                                 uplink=uplink_trace,
                                                 downlink=downlink_trace,
                                                 mahimahi_command=self.config['mahimahi_command'])

        results_cmd = self.fig_2_results_cmd_fmt.format(log_file=self.uplink_log_file_path,
                                                   results_file=self.results_file_path)

        cleanup_commands = self.config['cleanup_commands']
        return prep_commands + [mahimahi_cmd] + cleanup_commands + [results_cmd]

    def show(self):
        """Pretty print thyself
        
        """
        print(" ======== Protocol ======== \n")
        print("            Name: %s" % self.name)
        print("    Results path: %s" % self.results_file_path)
        print(" Uplink log path: %s" % self.uplink_log_file_path)
        pprint.pprint(self.config)

    
      
