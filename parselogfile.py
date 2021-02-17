#!/usr/bin/env python3
import argparse
import log.parseeyefile as logparser
import time
import sys

if __name__ == "__main__":

    cmdparser = argparse.ArgumentParser()
    cmdparser.add_argument(
        "filenames",
        nargs="+",
        help="The files to be parsed"
    )

    cmdargs = cmdparser.parse_args()
    files = cmdargs.filenames

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
            print (msg.format(fname, tend - tzero))
        else:
            msg = "unable to parse {}, because:\n{}"
            tabbed_errors = ["\t" + str(error) + "\n" for error in pr.getErrors()]
            print(msg.format(fname, tabbed_errors))
