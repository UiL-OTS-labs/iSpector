#!/usr/bin/perl

use strict;
use warnings;


open (RFIX, ">rfix.csv") or die "unable to open rfilehandle";
open (LFIX, ">lfix.csv") or die "unable to open lfilehandle";

while (<>) {
    
    if (/^2\s+.*$/) {
        print LFIX $_;
    }
    elsif(/^3\s+.*$/) {
        print RFIX $_;
    }
}

close(RFIX);
close(LFIX);
