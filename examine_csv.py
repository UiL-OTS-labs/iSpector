#!/usr/bin/env python

import arguments as cmdargs
from parseeyefile import *
from eyeexperiment import *
from eyedata import *
from eyeoutput import showOutput, createFixPic
import re
import sys
import os.path

def examine(fnames):
    '''
    Examine every item in args.
    @args the input files to examine.
    '''
    for i in fnames:
        #experiment = None
        pr = parseEyeFile(i)
        entries = pr.getEntries()
        if not entries :
            errors = pr.getErrors()
            for j in errors:
                print j[0] +"\t" + str(j[1])
            exit( "unable to parse: " + i)
        experiment = EyeExperiment(entries)
        for t in experiment.trials:
            try:
                eyedata = EyeData(cmdargs.ARGS.threshold,
                        cmdargs.ARGS.nthres, cmdargs.ARGS.smooth)
                if t.containsGazeData() == True:
                    eyedata.processTrial(t, True)
                    showOutput(eyedata, t.stimulus, cmdargs.ARGS.smooth,
                        cmdargs.ARGS.compare, cmdargs.ARGS.draw_saccades)
                if t.containsFixations():
                    createFixPic(t)
            except IOError as e:
                print e

def extractForFixation(fnames):
    '''
    Extracts the output of an zep experiment.
    @fnames the input files to examine.
    '''
    for name in fnames:
        #experiment = None
        entries = parseEyeFile(name)
        if not entries :
            exit( "unable to parse: " + name)

        # Remove fixations and saccades
        entries = LogEntry.removeEyeEvents(entries)
        if cmdargs.ARGS.extract_left and cmdargs.ARGS.extract_right:
            sys.stderr.write(
                "examine_csv by default extracts left and right eye\n"
                )
        elif cmdargs.ARGS.extract_left:
            entries = LogEntry.removeRightGaze(entries)
        elif cmdargs.ARGS.extract_right:
            entries = LogEntry.removeLeftGaze(entries)

        experiment = EyeExperiment(entries)

        # find our own saccades and fixations
        for t in experiment.trials:
            if t.containsGazeData() == True:
                eyedata = EyeData(cmdargs.ARGS.threshold,
                        cmdargs.ARGS.nthres, cmdargs.ARGS.smooth)
                eyedata.processTrial(t, True)
                lfixes, rfixes = eyedata.getFixations()
                rsacs , lsacs  = eyedata.getSaccades()
                entries.extend(lfixes)
                entries.extend(rfixes)
                entries.extend(lsacs)
                entries.extend(rsacs)
    
        root, ext   = os.path.splitext(name)
        newsuf      = "_fix.asc"
        outputfile  = root + newsuf

        # handing file already exists case.
        if os.path.exists(outputfile):
            try:
                answer = raw_input( "The file \"" + outputfile + "\" exist overwrite (y/n) [y]?")
                if answer in ["", "y","Y"]: pass
                else : exit("Not writing to: " + outputfile)
            except EOFError as e:
                exit("Unable to open " + outputfile)

        saveForFixation(entries, outputfile)

if __name__ == "__main__":
    cmdargs.parseCmdLine()
    if cmdargs.ARGS.extract :
        extractForFixation(cmdargs.ARGS.files)        
    else : 
        examine(cmdargs.ARGS.files)
