#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from optparse import OptionParser


class KlogStatist():

    '''Kmsg log statisc core implment.'''

    def __init__(self):

        self._scount = {}
        self._levcount = {}
        self._account = 0
        self._incount = 0
        self._filter =re.compile("(<\d+?>)\[[ 0-9.]+\].+?(\[.*)")
        self.r1 = re.compile("0x[0-9a-f]{1,}", re.I)
        self.r2 = re.compile("[0-9a-f]{6,}", re.I)
        self.r3 = re.compile("\d+", re.I)

    def parse_filelist(self, options, filelist):

        for fname in filelist:
            try:
                with open(fname, "r") as fobj:
                    self.parse_file(options, fobj)
            except Exception, ex:
                print >> sys.stderr, ex

        #print self._levcount
        #print self._tagcount
        #print self._levtag_count


    def parse_file(self, options, fobj):

        for line in fobj:
            self._incount += 1

            r = self._filter.match(line)
            if not r:
                # print line
                continue

            level, content = r.groups()
            if not options.level_all and not level in options.level:
                continue

            self._account += 1
            content = self.r1.sub("_HEX_", content)
            content = self.r2.sub("_HEX_", content)
            content = self.r3.sub("_NUM_", content)

            self._levcount[level] = self._levcount.get(level, 0)  + 1

            key = (level, content)
            self._scount[key] = self._scount.get(key, 0) + 1


    def output(self, maxline, threshold, fobj):
        stdout_bak = sys.stdout
        sys.stdout = fobj

        print " SUMMARY ".center(60, "=")
        print "Input lines:", self._incount
        print "Accept lines:", self._account
        
        print " LEVEL COUNTER ".center(60, "=")
        sortedDict = sorted(self._levcount.iteritems(), key=lambda d: d[1], reverse=True)

        for k, v in sortedDict:
            print str(v).ljust(10), k

        print " KLOG COUNTER ".center(60, "=")
        sortedDict = sorted(self._scount.iteritems(), key=lambda d: d[1], reverse=True)
        c = 0
        for k, v in sortedDict:
            if v >= threshold and c < maxline:
                c += 1
                print  str(v).ljust(10), k[0], k[1]
            else:
                break

        sys.stdout.flush()
        sys.stdout = stdout_bak

def main(argv):
    parser = OptionParser(usage="%prog [optinos] [kmsg.txt ...]")
    parser.add_option("-l", "--level",
                      dest="level",
                      default="all",
                      help="Specify level numbers, 'all' means '0123456789' "
                      )
    parser.add_option("-m", "--maxline",
                      action="store",
                      type='int',
                      dest="maxline",
                      default=100,
                      help="Specify max lines to output, default is 100"
                      )
    parser.add_option("-t", "--threshold",
                      action="store",
                      type='int',
                      dest="threshold",
                      default=0,
                      help="Counter great than threshold will be output"
                      )
    parser.add_option("-f", "--filename",
                      action="store",
                      dest="filename",
                      help="Statisc result write to FILENAME, default is stdout"
                      )
    (options, args) = parser.parse_args()

    #print options
    #print args

    options.level = options.level.upper()
    if options.level == "ALL":
        options.level_all = True

    ts = KlogStatist()

    if len(args) == 0:
        ts.parse_file(options, sys.stdin)
    else:
        ts.parse_filelist(options, args)


    try:

        if options.filename is None:
            outfile = sys.stdout
        else:
            outfile = open(options.filename, "w")
        ts.output(options.maxline, options.threshold, outfile)
    except Exception, ex:
        print >> sys.stderr, ex

if __name__ == "__main__":
        main(sys.argv)

