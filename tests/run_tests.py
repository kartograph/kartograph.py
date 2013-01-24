from kartograph import Kartograph
import sys
from os import mkdir, remove
from os.path import exists, splitext, basename
from glob import glob
from kartograph.options import read_map_config

for path in ('data', 'results'):
    if not exists(path):
        mkdir(path)

if not exists('data/ne_50m_admin_0_countries.shp'):
    # download natural earth shapefile
    print 'I need a shapefile to test with. Will download one from naturalearthdata.com\n'
    from subprocess import call
    call(['wget', 'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_countries.zip'])
    print '\nUnzipping...\n'
    call(['unzip', 'ne_50m_admin_0_countries.zip', '-d', 'data'])

passed = 0
failed = 0

log = open('log.txt', 'w')

for fn in glob('configs/*.*'):
    fn_parts = splitext(basename(fn))
    print 'running text', basename(fn), '...',
    try:
        cfg = read_map_config(open(fn))
        K = Kartograph()
        css_url = 'styles/' + fn_parts[0] + '.css'
        css = None
        if exists(css_url):
            css = open(css_url).read()
        svg_url = 'results/' + fn_parts[0] + '.svg'
        if exists(svg_url):
            remove(svg_url)
        K.generate(cfg, 'results/' + fn_parts[0] + '.svg', preview=False, format='svg', stylesheet=css)
        print 'ok.'
        passed += 1
    except Exception, e:
        import traceback
        ignore_path_len = len(__file__) - 7
        exc = sys.exc_info()
        log.write('\n\nError in test %s' % fn)
        for (filename, line, func, code) in traceback.extract_tb(exc[2]):
            log.write('  %s, in %s()\n  %d: %s\n' % (filename, func, line, code))
        log.write('\n')
        log.write(str(e))
        print 'failed.'
        failed += 1

print 'passed: %d\nfailed: %d' % (passed, failed)
