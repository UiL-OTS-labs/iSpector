#!/usr/bin/env python3
import argparse
import log.parseeyefile as logparser
import log.eyeexperiment
import time
import sys

if __name__ == "__main__":

    cmdparser = argparse.ArgumentParser()
    cmdparser.add_argument(
        "filenames",
        nargs="+",
        help="The files to be parsed"
    )
    cmdparser.add_argument(
        '-e', "--experiment", action='store_true',
        help='Next to parsing the log also turn in into an experiment'
    )

    cmdargs = cmdparser.parse_args()
    files = cmdargs.filenames

    msg = "Turning the entries of {} into an experiment took {} seconds"

    for fname in files:
        tzero = time.time()
        try:
            parseresult = logparser.parseEyeFile(fname)
        except IOError as e:
            print(str(e), file=sys.stderr)
            continue
        tend = time.time()
        entries = parseresult.getEntries()
        if entries:
            msg = "Parsed {} in {} seconds"
            print(msg.format(fname, tend - tzero))
        else:
            msg = "unable to parse {}, because:\n{}"
            pr = parseresult
            tabbed_errors = [
                "\t" + str(error) + "\n" for error in pr.getErrors()
            ]
            print(msg.format(fname, tabbed_errors))
            continue
        if cmdargs.experiment:
            tzero = time.time()
            experiment = log.eyeexperiment.EyeExperiment(entries)
            tend = time.time()
            print(msg.format(fname, tend - tzero))
