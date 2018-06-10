#
# Defines base class for a Congestion Control
# protocol used to run experiments for our
# reproduction of the ABC paper.
#

import json
import pprint
import collections
import os

class CCProtocol:

    fig_2_base_cmd_fmt = "mm-delay {delay} \
            mm-link --once --{target_link}-log={log} \
            {queue_args} \
            {uplink} {downlink} \
            -- bash -c '{mahimahi_command}'"

    fig_2_results_cmd_fmt = "mm-throughput-graph 500 {log_file} > \
            {graph_file} 2> {results_file}"

    mahimahi_queue_args_fmt = "--{target_link}-queue={queue} \
            --{target_link}-queue-args=\"{queue_args}\""

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
        with open(os.path.expanduser(config_file_path)) as f:
            self.config = json.load(f)

        self.results_file_path = results_file_path
        self.uplink_log_file_path = uplink_log_file_path

        for arg in extra_args:
            self.config[arg] = extra_args[arg]

    def get_figure1_cmds(self, mm_delay, uplink_trace, downlink_trace, args):
        """ Returns list of commands to run to generate Figure 1 results.
        """

        # These are actually exactly the same as figure 2 commands.
        return self.get_figure2_cmds(mm_delay, uplink_trace, downlink_trace, args)

    def get_figure2_cmds(self, mm_delay, uplink_trace, downlink_trace, args):
        """ Returns ordered dictionary of commands
        to run to generate Figure 2 results.
        """
        target_link = self.config.get('target_link', 'uplink')
        if self.config['uplink_queue'] == '':
            queue_args = ''
        else:
            queue_args = self.mahimahi_queue_args_fmt.format(
                    target_link=target_link,
                    queue=self.config['uplink_queue'],
                    queue_args=self.config['uplink_queue_args']
            )

        prep_commands = self.config['prep_commands']
        if target_link == 'downlink':
            uplink_trace, downlink_trace = (downlink_trace, uplink_trace)
        mahimahi_cmd = self.fig_2_base_cmd_fmt.format(
                target_link=target_link, delay=str(mm_delay), log=self.uplink_log_file_path,
                queue_args=queue_args, uplink=uplink_trace,
                downlink=downlink_trace, mahimahi_command=self.config['mahimahi_command']
        )

        graph_out = '/dev/null'
        if args.print_graph:
            graph_out = 'graphs/%s_graph.svg' % self.config['name']
        results_cmd = self.fig_2_results_cmd_fmt.format(
                log_file=self.uplink_log_file_path, results_file=self.results_file_path,
                graph_file=graph_out)

        cleanup_commands = self.config['cleanup_commands']

        commands = [("prep", prep_commands),
                    ("mahimahi", [mahimahi_cmd]),
                    ("cleanup", cleanup_commands),
                    ("results", [results_cmd])]

        return collections.OrderedDict(commands)

    def show(self):
        """Pretty print thyself

        """
        print(" ======== Protocol ======== \n")
        print("            Name: %s" % self.name)
        print("    Results path: %s" % self.results_file_path)
        print(" Uplink log path: %s" % self.uplink_log_file_path)
        pprint.pprint(self.config)
