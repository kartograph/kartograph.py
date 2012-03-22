"""
command line interface for kartograph
"""

from kartograph import Kartograph
from cartogram import Cartogram
import sys, os, os.path, getopt, json, time


def main():
    start = time.time()

    from errors import KartographError

    if len(sys.argv) < 3:
        print "try: kartograph svg map-config.yaml"
        sys.exit(1)

    command = sys.argv[1]

    if command in ("generate", "kml", "svg"):

        cfg = {}
        output = None
        opt_src = None
        opts, args = getopt.getopt(sys.argv[3:], 'c:o:', ['config=', 'output='])
        for o, a in opts:
            if o in ('-c', '--config'):
                opt_src = a
            elif o in ('-o', '--output'):
                output = a

        if opt_src is None and len(sys.argv) > 2:
            opt_src = sys.argv[2]
        else:
            raise KartographError('you need to pass a map configuration (json/yaml)')

        # check and load map configuration
        if os.path.exists(opt_src):
            t = open(opt_src, 'r').read()
            if opt_src[-5:].lower() == '.json':
                cfg = json.loads(t)
            elif opt_src[-5:].lower() == '.yaml':
                import yaml
                cfg = yaml.load(t)
            else:
                raise KartographError('supported config formats are .json and .yaml')
        else:
            raise KartographError('configuration not found')

        K = Kartograph()

        try:
            if command == "kml":
                K.generate_kml(cfg, output)
            else:
                K.generate(cfg, output)
        except KartographError as e:
            print e

        elapsed = (time.time() - start)

        print 'execution time: %.4f secs' % elapsed
        sys.exit(0)

    elif command == "cartogram":

        map = sys.argv[2]
        attr = sys.argv[3]
        data = sys.argv[4]
        key = sys.argv[5]
        val = sys.argv[6]

        C = Cartogram()
        C.generate(map, attr, data, key, val)


if __name__ == "__main__":
    main()
