#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re

class AvcCore():

    '''根据AVC出错日志生成.te文本'''

    def __init__(self):
        self._avc = {}
        self._incout = 0
        self._outcount = 0

    def parseFile(self, file):

        avclines = [line for line in file if "avc: denied" in line]
        self._incout += len(avclines)

        m = re.compile(".*{ (\w+) }.*scontext=u:r:(\w+):s0\s+tcontext=u:r:(\w+):s0\s+tclass=(\w+)")

        for line in avclines:
            r = m.match(line)
            if not r :
                # 格式异常的avc出错行
                #print line
                continue

            self._outcount += 1

            perm, scontext, tcontext, tclass = r.groups()
            #print(r.groups())

            if not scontext in self._avc:
                tcitem = (tcontext, tclass)
                permset = [perm]
                sitem = {tcitem : permset}
                self._avc[scontext] = sitem
            else:
                sitem = self._avc[scontext]
                tcitem = (tcontext, tclass)
                if (tcitem not in sitem):
                    permset = [perm]
                    sitem[tcitem] = permset
                else:
                    permset = sitem[tcitem]
                    permset.append(perm)

        # 去除重复的权限
        for skey in self._avc:
            sitem = self._avc[skey]
            for tckey in sitem:
                sitem[tckey] = list(set(sitem[tckey]))


    def output(self):
        print "avc denied line: ", self._incout
        print "accept line: ", self._outcount

        for skey in self._avc:
            sitem = self._avc[skey]

            print
            print("# %s.te" % (skey,))
            for tckey in sorted(sitem.keys()):
                tcontext, tclass = tckey
                print("allow %s %s:%s {%s}" % (skey, tcontext, tclass, " ".join(sitem[tckey])))


def main(argv):
    file = None
    if len(argv) == 1:
        file = sys.stdin
    else:
        try:
            file = open(argv[1], "r")
        except Exception as e:
            print "open file error:", e
            sys.exit(1)

    core = AvcCore()
    core.parseFile(file)
    core.output()


if __name__ == "__main__":
        main(sys.argv)

