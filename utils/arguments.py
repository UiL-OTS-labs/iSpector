#!/usr/bin/env python

##
# \file arguments.py
#
# In this file handeling of commandline arguments is handled.

import argparse
import matplotlib
from gui.ispectorgui import MainGuiModel
import gui.ispectorgui

PARSER = None
ARGS   = None

LOGO = "iSpectorLogo.svg"

class TestActionOption(argparse.Action):

    ## message to format message in case of a invalid action.
    message = "choose one of {0}"

    def __call__(self, parser, namespace, value, option_string=None):
        valid = MainGuiModel.VALID_ACTIONS
        if value:
            if value not in valid:
                message = TestActionOption.message\
                           .format(", ".join(valid))
                raise argparse.ArgumentError(self, message)
        setattr(namespace, self.dest, value)

def _addArguments(p):
    '''
    Adds arguments to the parser
    @param p the parser
    '''
    #these are options that modify the behavior of the program
    p.add_argument('-s', '--smooth',
        help="Enable smoothing", action="store_true"
        )
    p.add_argument('-w', '--swin',
        help="Size of the smoothing window, the value must be odd", type=int,
         default=7, choices=gui.ispectorgui.SMOOTH_WINDOW_CHOICES
        )
    p.add_argument('-o', '--sorder',
        help='Polynomial order of function used to smooth see wiki on Savitzky-Golayfilter filter',
        type=int, default=2
        )
    p.add_argument('-b', '--backend', help="specify the matplotlib backend")
    p.add_argument('-m', '--threshold', default="median",
        help='Method for finding a threshold for the fixations must be mean or median'
        )
    p.add_argument('-n', '--nthres', default=4.0, type=float,
        help='Threshold for saccade or fixation nthres*the median or mean of the eye velocity'
        )
    p.add_argument('--draw-saccades', action="store_true",
        help="draw saccades instead of fixations"
        )
    p.add_argument('-c', '--compare', action="store_true",
        help='Compares our fixations with the logged ones.'
        )
    
    p.add_argument('-a', '--action', type=str, default="inspect", action=TestActionOption,
        help='Doesn\'t inspect the file, but detects fixations and saccades and logs those compatible for fixation.'
        )
    p.add_argument('-l', '--extract-left', action="store_true",
        help='Extract only the left-gaze and fixations'
        )
    p.add_argument('-r', '--extract-right', action="store_true",
        help='Extract only the right-gaze and fixations'
        )
    p.add_argument('-d', '--output-dir', type=str, default="", help="specify the output directory")
    p.add_argument('--stim-dir', type=str, default="", help="specify the directory where the stimuli can be found.")
    
    #these are positional arguments
    p.add_argument('files', nargs='*',
        help="The input files to examine the eyemovement data.")

def parseCmdLine():
    ''' Call only once to intialize the argument and options. '''
    PARSER = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    _addArguments(PARSER)
    global ARGS
    ARGS = PARSER.parse_args()
    if ARGS.backend:
        matplotlib.use(ARGS.backend)

def parseCmdLineKnown():
    ''' Call only once to intialize the argument and options.
        This command line only parses the options it kwows
        returns unparsed options
    '''
    PARSER = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    _addArguments(PARSER)
    global ARGS
    ARGS, unparsed_options = PARSER.parse_known_args()
    if ARGS.backend:
        matplotlib.use(ARGS.backend)
    return unparsed_options
