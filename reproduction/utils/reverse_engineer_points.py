#!/usr/bin/python

from collections import namedtuple
import math
from pprint import pprint

Figure = namedtuple('Figure', ['name', 'ylim', 'xscale',
    'yscale', 'x_200', 'x_300', 'height', 'points'])

FIGURE2A = Figure(
    name='Figure 2A',
    ylim=(.3, 1.0),
    xscale='log',
    yscale='linear',
    x_200=100,
    x_300=223.5,
    height=312.86,
    points= {
        'abc': (87.5, 263.5),
        'sprout':(59, 44),
        'cubicpie':(20, 102),
        'cubiccodel':(64.3, 142.5),
        'verus': (274.5, 251.5),
        'vegas':(263, 273.25),
        'bbr': (371, 286),
        'cubic': (344, 304)
    }
)

FIGURE2B = Figure(
    name='Figure 2B',
    ylim=(.3, 1.0),
    xscale='log',
    yscale='linear',
    x_200=207.5,
    x_300=616,
    height=1065,
    points= {
        'abc': (180, 847),
        'sprout':(94, 125),
        'cubicpie':(60, 382),
        'cubiccodel':(245, 488),
        'verus': (954, 794),
        'vegas':(1300, 958),
        'bbr': (1280, 962),
        'cubic': (1240, 1026)
    }
)

FIGURES = [FIGURE2A, FIGURE2B]

def get_pixel_scale(x_200, x_300):
    log_200 = math.log(200, 10)
    log_300 = math.log(300, 10)
    return (log_300 - log_200) / (x_300 - x_200)

def get_original_val(x, pixel_scale, x_200):
    log_200 = math.log(200, 10)
    return math.pow(10, log_200 + pixel_scale * (x - x_200))

if __name__ == '__main__':
    for f in FIGURES:
        print('{}:'.format(f.name))
        points = dict()

        pixel_scale = get_pixel_scale(f.x_200, f.x_300)
        ymin = f.ylim[0]
        ydif = f.ylim[1] - f.ylim[0]
        for proto, (x, y) in f.points.items():
            x = get_original_val(x, pixel_scale, f.x_200)
            y = (float(y) / f.height) * ydif + ymin
            points[proto] = (x, y)

        pprint(points)
