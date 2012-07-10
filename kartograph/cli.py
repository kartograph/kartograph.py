#!/usr/bin/env python
"""
command line interface for kartograph
"""

import argparse
import os.path
from options import read_map_descriptor


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


parser = argparse.ArgumentParser(prog='kartograph', description='generating svg maps from shapefiles (dpa edition 2)')

parser.add_argument('config', type=argparse.FileType('r'), help='the configuration for the map. accepts json and yaml.')
parser.add_argument('--output', '-o', metavar='FILE', type=argparse.FileType('w'), help='the file in which the map will be stored')
parser.add_argument('--verbose', '-v', nargs='?', metavar='', const=True, help='verbose mode')
parser.add_argument('--format', '-f', metavar='svg|kml', help='output format, if not specified it will be guessed from output filename or default to svg')
parser.add_argument('--preview', '-p', nargs='?', metavar='', const=True, help='opens the generated svg for preview')

from kartograph import Kartograph
import time
import sys
import os


def render_map(args):
    cfg = read_map_descriptor(args.config)
    K = Kartograph()
    if args.format:
        format = args.format
    elif args.output:
        format = os.path.splitext(args.output.name)[1][1:]
    else:
        format = 'svg'
    try:

        # generate the map
        K.generate(cfg, args.output, preview=args.preview, format=format)

    except Exception, e:
        print_error(e)
        exit(-1)

parser.set_defaults(func=render_map)


def print_error(e):
    import traceback
    ignore_path_len = len(__file__) - 7
    exc = sys.exc_info()
    for (filename, line, func, code) in traceback.extract_tb(exc[2]):
        if filename[:len(__file__) - 7] == __file__[:-7]:
            print '  \033[1;33;40m%s\033[0m, \033[0;37;40min\033[0m %s()\n  \033[1;31;40m%d:\033[0m \033[0;37;40m%s\033[0m' % (filename[ignore_path_len:], func, line, code)
        else:
            print '  %s, in %s()\n  %d: %s' % (filename, func, line, code)
    print
    print e

def main():
    start = time.time()

    try:
        args = parser.parse_args()
    except IOError, e:
        parser.print_help()
        print '\nIOError:', e
    except Exception, e:
        parser.print_help()
        print '\nError:', e
    else:
        args.func(args)

    elapsed = (time.time() - start)
    print 'execution time: %.3f secs' % elapsed
    sys.exit(0)


if __name__ == "__main__":
    main()
