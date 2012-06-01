#!/usr/bin/env python
"""
command line interface for kartograph
"""

import argparse
import os.path
import json
from errors import KartographError


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

parser = argparse.ArgumentParser(prog='kartograph', description='generating svg maps from shapefiles')
#parser.add_argument('command', type=str, choices=['svg', 'kml', 'generate'], help='specifies what kartograph is supposed to do')

subparsers = parser.add_subparsers(help='sub-command help')

parser_svg = subparsers.add_parser('svg', help='generates svg map')
parser_svg.add_argument('config', type=argparse.FileType('r'), help='the configuration for the map. accepts json and yaml.')
parser_svg.add_argument('--output', '-o', metavar='FILE', type=argparse.FileType('w'), help='the file in which the map will be stored')

parser_kml = subparsers.add_parser('kml', help='generates kml map')
parser_kml.add_argument('config', type=argparse.FileType('r'), help='the configuration for the map. accepts json and yaml.')
parser_kml.add_argument('--output', '-o', metavar='FILE', type=argparse.FileType('w'), help='the file in which the map will be stored')

parser_cartogram = subparsers.add_parser('cartogram', help='cartogram tool')
parser_cartogram.add_argument('map', type=argparse.FileType('r'), help='the map svg the cartogram should be added to')
parser_cartogram.add_argument('layer', type=str, help='id of the layer the cartogram should be generated from')
parser_cartogram.add_argument('attr', type=str, help='the attribute that identifies the map features')
parser_cartogram.add_argument('data', type=argparse.FileType('r'), help='csv file')
parser_cartogram.add_argument('key', type=str, help='the column that contains the keys to identify features')
parser_cartogram.add_argument('val', type=str, help='the column that contains the values for each feature')


from kartograph import Kartograph
from cartogram import Cartogram
import time
import sys


def parse_config(f):
    content = f.read()
    if f.name[-5:].lower() == '.json':
        try:
            cfg = json.loads(content)
        except Exception, e:
            raise KartographError('parsing of json map configuration failed.\n' + e)
        else:
            return cfg
    elif f.name[-5:].lower() == '.yaml':
        import yaml
        try:
            cfg = yaml.load(content)
        except Exception, e:
            raise KartographError('parsing of yaml map configuration failed.\n' + e)
        else:
            return cfg
    else:
        raise KartographError('supported config formats are .json and .yaml')


def svg(args):
    cfg = parse_config(args.config)
    K = Kartograph()
    try:
        K.generate(cfg, args.output)
    except Exception, e:
        import traceback, sys
        ignore_path_len = len(__file__) - 7
        exc = sys.exc_info()
        for (filename, line, func, code) in traceback.extract_tb(exc[2]):
            if filename[:len(__file__) - 7] == __file__[:-7]:
                print '  \033[1;33;40m%s\033[0m, \033[0;37;40min\033[0m %s()\n  \033[1;31;40m%d:\033[0m \033[0;37;40m%s\033[0m' % (filename[ignore_path_len:], func, line, code)
            else:
                print '  %s, in %s()\n  %d: %s' % (filename, func, line, code)
        print
        print e
        exit(-1)


def kml(args):
    cfg = parse_config(args.config)
    K = Kartograph()
    try:
        K.generate_kml(cfg, args.config)
    except KartographError, e:
        print e
        exit(-1)


def cartogram(args):
    C = Cartogram()
    C.generate(args.map, args.attr, args.data, args.key, args.val)


parser_svg.set_defaults(func=svg)
parser_kml.set_defaults(func=kml)
parser_cartogram.set_defaults(func=cartogram)


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
