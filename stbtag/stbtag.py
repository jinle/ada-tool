#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from optparse import OptionParser


class BtagStatist():

    '''Buff log statisc core implment.'''

    def __init__(self):
        self._avc = {}
        self._levcount = {}
        self._tagcount = {}
        self._levtag_count = {}
        self._incount = 0
        self._account = 0
        self._outcount = 0
        self._filter =re.compile(".* ([A-Z]) (.+?):.*")


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


            level, tag = r.groups()

            if not options.level_all and not level in options.level:
                continue

            self._account += 1

            # print(r.groups())
            if level in self._levcount:
                self._levcount[level] += 1
            else:
                self._levcount[level] = 1

            if tag in self._tagcount:
                self._tagcount[tag] += 1
            else:
                self._tagcount[tag] = 1

            lev_tag = (level, tag)
            if lev_tag in self._levtag_count:
                self._levtag_count[lev_tag] += 1
            else:
                self._levtag_count[lev_tag] = 1

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

        print " TAG COUNTER ".center(60, "=")
        sortedDict = sorted(self._tagcount.iteritems(), key=lambda d: d[1], reverse=True)
        c = 0
        for k, v in sortedDict:
            if v >= threshold and c < maxline:
                c += 1
                print str(v).ljust(10), k
            else:
                break


        print " LEVEL:TAG COUNTER ".center(60, "=")
        sortedDict = sorted(self._levtag_count.iteritems(), key=lambda d: d[1], reverse=True)
        c = 0
        for k, v in sortedDict:
            if v >= threshold and c < maxline:
                c += 1
                print str(v).ljust(10), ":".join(k).ljust(40)
            else:
                break

        sys.stdout.flush()
        sys.stdout = stdout_bak

def main(argv):
    parser = OptionParser(usage="%prog [optinos] [logcat.txt ...]")
    parser.add_option("-l", "--level",
                      dest="level",
                      default="all",
                      help="Specify level alphas, 'all' means 'VDIWEF' "
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

    bs = BtagStatist()

    if len(args) == 0:
        bs.parse_file(options, sys.stdin)
    else:
        bs.parse_filelist(options, args)


    try:

        if options.filename is None:
            outfile = sys.stdout
        else:
            outfile = open(options.filename, "w")
        bs.output(options.maxline, options.threshold, outfile)
    except Exception, ex:
        print >> sys.stderr, ex

if __name__ == "__main__":
        main(sys.argv)

