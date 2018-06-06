python experiment.py --schemes sprout cubiccodel cubicpie abc vegas verus bbr cubic --experiment figure2a --csv-out figure2a_results.csv
python figure2_plot.py figure2a_results.csv figure2a_plot.svg -o 2a
python experiment.py --schemes sprout cubiccodel cubicpie abc vegas verus bbr cubic --experiment figure2b --csv-out figure2b_results.csv
python figure2_plot.py figure2b_results.csv figure2b_plot.svg -o 2b
