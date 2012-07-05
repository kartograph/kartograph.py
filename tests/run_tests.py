
from kartograph import Kartograph
import sys
from os import mkdir
from os.path import exists, splitext, basename
from glob import glob
from kartograph.options import read_map_descriptor

for path in ('data', 'results'):
    if not exists(path):
        mkdir(path)

if not exists('data/ne_50m_admin_0_countries.shp'):
    # download natural eath shapefile
    pass

passed = 0
failed = 0

log = open('log.txt', 'w')

for fn in glob('configs/*.*'):
    fn_parts = splitext(basename(fn))
    try:
        cfg = read_map_descriptor(open(fn))
        K = Kartograph()
        K.generate(cfg, 'results/' + fn_parts[0] + '.svg', preview=False, format='svg')
        passed += 1
    except Exception, e:
        import traceback
        ignore_path_len = len(__file__) - 7
        exc = sys.exc_info()
        log.write('Error in test %s' % fn)
        for (filename, line, func, code) in traceback.extract_tb(exc[2]):
            log.write('  %s, in %s()\n  %d: %s\n' % (filename, func, line, code))
        log.write('\n')
        log.write(str(e))
        failed += 1

print 'passed: %d\nfailed: %d' % (passed, failed)
