
from options import parse_options
from shapely.geometry import Polygon, LineString, MultiPolygon
from errors import *
from copy import deepcopy
from renderer import SvgRenderer
from mapstyle import MapStyle
from map import Map
import os


# Kartograph
# ----------

verbose = False

# These renderers are currently available. See [renderer/svg.py](renderer/svg.html)

_known_renderer = {
    'svg': SvgRenderer
}


class Kartograph(object):
    def __init__(self):
        self.layerCache = {}
        pass

    def generate(self, opts, outfile=None, format='svg', preview=None, stylesheet=None):
        """
        Generates a the map and renders it using the specified output format.
        """
        if preview is None:
            preview = outfile is None

        # Create a deep copy of the options dictionary so our changes will not be
        # visible to the calling application.
        opts = deepcopy(opts)

        # Parse the options dictionary. See options.py for more details.
        parse_options(opts)

        # Create the map instance. It will do all the hard work for us, so you
        # definitely should check out [map.py](map.html) for all the fun stuff happending
        # there..
        _map = Map(opts, self.layerCache, format=format)

        # Check if the format is handled by a renderer.
        format = format.lower()
        if format in _known_renderer:
            # Create a stylesheet
            style = MapStyle(stylesheet)
            # Create a renderer instance and render the map.
            renderer = _known_renderer[format](_map)
            renderer.render(style, opts['export']['prettyprint'])

            if preview:
                if 'KARTOGRAPH_PREVIEW' in os.environ:
                    command = os.environ['KARTOGRAPH_PREVIEW']
                else:
                    commands = dict(win32='start', win64='start', darwin='open', linux2='xdg-open')
                    import sys
                    if sys.platform in commands:
                        command = commands[sys.platform]
                    else:
                        sys.stderr.write('don\'t know how to preview SVGs on your system. Try setting the KARTOGRAPH_PREVIEW environment variable.')
                        print renderer
                        return
                renderer.preview(command)
            # Write the map to a file or return the renderer instance.
            if outfile is None:
                return renderer
            elif outfile == '-':
                print renderer
            else:
                renderer.write(outfile)
        else:
            raise KartographError('unknown format: %s' % format)


# Here are some handy methods for debugging Kartograph. It will plot a given shapely
# geometry using matplotlib and descartes.
def _plot_geometry(geom, fill='#ffcccc', stroke='#333333', alpha=1, msg=None):
    from matplotlib import pyplot
    from matplotlib.figure import SubplotParams
    from descartes import PolygonPatch

    if isinstance(geom, (Polygon, MultiPolygon)):
        b = geom.bounds
        geoms = hasattr(geom, 'geoms') and geom.geoms or [geom]
        w, h = (b[2] - b[0], b[3] - b[1])
        ratio = w / h
        pad = 0.15
        fig = pyplot.figure(1, figsize=(5, 5 / ratio), dpi=110, subplotpars=SubplotParams(left=pad, bottom=pad, top=1 - pad, right=1 - pad))
        ax = fig.add_subplot(111, aspect='equal')
        for geom in geoms:
            patch1 = PolygonPatch(geom, linewidth=0.5, fc=fill, ec=stroke, alpha=alpha, zorder=0)
            ax.add_patch(patch1)
    p = (b[2] - b[0]) * 0.03  # some padding
    pyplot.axis([b[0] - p, b[2] + p, b[3] + p, b[1] - p])
    pyplot.grid(True)
    if msg:
        fig.suptitle(msg, y=0.04, fontsize=9)
    pyplot.show()


def _plot_lines(lines):
    from matplotlib import pyplot

    def plot_line(ax, line):
        filtered = []
        for pt in line:
            if not pt.deleted:
                filtered.append(pt)
        if len(filtered) < 2:
            return
        ob = LineString(line)
        x, y = ob.xy
        ax.plot(x, y, '-', color='#333333', linewidth=0.5, solid_capstyle='round', zorder=1)

    fig = pyplot.figure(1, figsize=(4, 5.5), dpi=90, subplotpars=SubplotParams(left=0, bottom=0.065, top=1, right=1))
    ax = fig.add_subplot(111, aspect='equal')
    for line in lines:
        plot_line(ax, line)
    pyplot.grid(False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_frame_on(False)
    return (ax, fig)


def _debug_show_features(features, message=None):
    from descartes import PolygonPatch
    from matplotlib import pyplot
    from matplotlib.figure import SubplotParams

    fig = pyplot.figure(1, figsize=(9, 5.5), dpi=110, subplotpars=SubplotParams(left=0, bottom=0.065, top=1, right=1))
    ax = fig.add_subplot(111, aspect='equal')
    b = (100000, 100000, -100000, -100000)
    for feat in features:
        if feat.geom is None:
            continue
        c = feat.geom.bounds
        b = (min(c[0], b[0]), min(c[1], b[1]), max(c[2], b[2]), max(c[3], b[3]))
        geoms = hasattr(feat.geom, 'geoms') and feat.geom.geoms or [feat.geom]
        for geom in geoms:
            patch1 = PolygonPatch(geom, linewidth=0.25, fc='#ddcccc', ec='#000000', alpha=0.75, zorder=0)
            ax.add_patch(patch1)
    p = (b[2] - b[0]) * 0.05  # some padding
    pyplot.axis([b[0] - p, b[2] + p, b[3], b[1] - p])
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_frame_on(True)
    if message:
        fig.suptitle(message, y=0.04, fontsize=9)
    pyplot.show()
