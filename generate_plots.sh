#!/bin/bash

mkdir -p plots
# figure 1
python reproduction/plotting/figure1_plot.py results-1/figure1.csv plots/figure1.svg
# figure 2a
python reproduction/plotting/figure2_plot.py results-1/figure2a.csv plots/figure2a.svg -o 2a -c -l -b
# figure 2b
python reproduction/plotting/figure2_plot.py results-1/figure2b.csv plots/figure2b.svg -o 2b -c -l
# bothlinks
python reproduction/plotting/figure2_plot.py results-1/bothlinks.csv plots/bothlinks.svg
# figure 2a + extra protos
python reproduction/plotting/figure2_plot.py results-1/figure2a.csv plots/figure2a_extra.svg -o 2a -c
# figure 2b + extra protos
python reproduction/plotting/figure2_plot.py results-1/figure2b.csv plots/figure2b_extra.svg -o 2b -c
