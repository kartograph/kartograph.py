
from kartograph.renderer import MapRenderer
from kartograph.errors import KartographError

# This script contains everything that is needed by Kartograph to finally
# render the processed maps into SVG files.
#

# The SVG renderer is based on xml.dom.minidom.
from xml.dom import minidom
from xml.dom.minidom import parse
import re


class SvgRenderer(MapRenderer):

    def render(self):
        """
        The render() method prepares a new empty SVG document and
        stores all the layer features into SVG groups.
        """
        self._init_svg_doc()
        self._store_layers_to_svg()

    def _init_svg_doc(self):
        # Load width and height of the map view
        # We add two pixels to the height to ensure that
        # the map fits.
        w = self.map.view.width
        h = self.map.view.height + 2

        # SvgDocument is a handy wrapper around xml.dom.minidom. It is defined below.
        svg = SvgDocument(
            width='%dpx' % w,
            height='%dpx' % h,
            viewBox='0 0 %d %d' % (w, h),
            enable_background='new 0 0 %d %d' % (w, h),
            style='stroke-linejoin: round; stroke:#000; fill:#f6f3f0;')

        defs = svg.node('defs', svg.root)
        style = svg.node('style', defs, type='text/css')
        css = 'path { fill-rule: evenodd; }\n#context path { fill: #eee; stroke: #bbb; } '
        svg.cdata(css, style)
        metadata = svg.node('metadata', svg.root)
        views = svg.node('views', metadata)
        view = svg.node('view', views,
            padding=str(self.map.options['bounds']['padding']), w=w, h=h)

        svg.node('proj', view, **self.map.proj.attrs())
        svg.node('bbox', view,
            x=round(self.map.src_bbox.left, 2),
            y=round(self.map.src_bbox.top, 2),
            w=round(self.map.src_bbox.width, 2),
            h=round(self.map.src_bbox.height, 2))

        ll = [-180, -90, 180, 90]
        if self.map.options['bounds']['mode'] == "bbox":
            ll = self.map.options['bounds']['data']
        svg.node('llbbox', view,
            lon0=ll[0], lon1=ll[2],
            lat0=ll[1], lat1=ll[3])
        self.svg = svg

    def _store_layers_to_svg(self):
        """
        store features in svg
        """
        svg = self.svg
        for layer in self.map.layers:
            if len(layer.features) == 0:
                print "ignoring empty layer", layer.id
                continue  # ignore empty layers
            g = svg.node('g', svg.root, id=layer.id)
            for feat in layer.features:
                node = self._render_feature(feat, layer.options['attributes'])
                if node is not None:
                    g.appendChild(node)
                else:
                    print "feature.to_svg is None", feat
            if 'styles' in layer.options:
                for prop in layer.options['styles']:
                    g.setAttribute(prop, str(layer.options['styles'][prop]))

    def _render_feature(self, feature, attributes=[]):
        node = self._render_geometry(feature.geometry)
        if node is None:
            return None

        for cfg in attributes:
            if 'src' in cfg:
                tgt = re.sub('(\W|_)+', '-', cfg['tgt'].lower())
                if cfg['src'] not in feature.props:
                    continue
                    #raise KartographError(('attribute not found "%s"'%cfg['src']))
                val = feature.props[cfg['src']]
                if isinstance(val, (int, float)):
                    val = str(val)
                node.setAttribute('data-' + tgt, val)
                if tgt == "id":
                    node.setAttribute('id', val)

            elif 'where' in cfg:
                # can be used to replace attributes...
                src = cfg['where']
                tgt = cfg['set']
                if len(cfg['equals']) != len(cfg['to']):
                    raise KartographError('attributes: "equals" and "to" arrays must be of same length')
                for i in range(len(cfg['equals'])):
                    if feature.props[src] == cfg['equals'][i]:
                        node.setAttribute('data-' + tgt, cfg['to'][i])

        if '__color__' in feature.props:
            node.setAttribute('fill', self.props['__color__'])
        return node

    def _render_geometry(self, geometry):
        from shapely.geometry import Polygon, MultiPolygon
        if isinstance(geometry, (Polygon, MultiPolygon)):
            return self._render_polygon(geometry)

    def _render_polygon(self, geometry):
        """ constructs a svg representation of a polygon """
        _round = self.map.options['export']['round']
        path_str = ""
        if _round is False:
            fmt = '%f,%f'
        else:
            fmt = '%.' + str(_round) + 'f'
            fmt = fmt + ',' + fmt

        geoms = hasattr(geometry, 'geoms') and geometry.geoms or [geometry]
        for polygon in geoms:
            if polygon is None:
                continue
            for ring in [polygon.exterior] + list(polygon.interiors):
                cont_str = ""
                kept = []
                for pt in ring.coords:
                    kept.append(pt)
                if len(kept) <= 3:
                    continue
                for pt in kept:
                    if cont_str == "":
                        cont_str = "M"
                    else:
                        cont_str += "L"
                    cont_str += fmt % pt
                cont_str += "Z "
                path_str += cont_str
        if path_str == "":
            return None
        path = self.svg.node('path', d=path_str)
        return path

    def write(self, filename):
        self.svg.write(filename)

    def preview(self):
        self.svg.preview()

    def __str__(self):
        return self.svg.tostring()


# SvgDocument
# -----------
#
# SVGDocument is a handy wrapper around xml.dom.minidom which allows us
# to quickly build XML structures. It is largely inspired by the SVG class
# of the [svgfig](http://code.google.com/p/svgfig/) project, which was
# used by one of the earlier versions of Kartograph.
#

class SvgDocument(object):

    # Of course, we need to create and XML document with all this
    # boring SVG header stuff added to it.
    def __init__(self, **kwargs):
        imp = minidom.getDOMImplementation('')
        dt = imp.createDocumentType('svg',
            '-//W3C//DTD SVG 1.1//EN',
            'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd')
        self.doc = imp.createDocument('http://www.w3.org/2000/svg', 'svg', dt)
        self.root = svg = self.doc.getElementsByTagName('svg')[0]
        svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
        svg.setAttribute('version', '1.1')
        svg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')
        _add_attrs(self.root, kwargs)

    # This is the magic of SvgDocument. Instead of having to do appendChild()
    # and addAttribute() for every node we create, we just call svgdoc.node()
    # which is smart enough to append itself to the parent if we specify one,
    # and also sets all attributes we pass as keyword arguments.
    def node(self, name, parent=None, **kwargs):
        el = self.doc.createElement(name)
        _add_attrs(el, kwargs)
        if parent is not None:
            parent.appendChild(el)
        return el

    # Sometimes we also need a <[CDATA]> block, for instance if we embed
    # CSS code in the SVG document.
    def cdata(self, data, parent=None):
        cd = minidom.CDATASection()
        cd.data = data
        if parent is not None:
            parent.appendChild(cd)
        return cd

    # Here we finally write the SVG file, and we're brave enough
    # to try to write it in Unicode.
    def write(self, outfile):
        if isinstance(outfile, str):
            outfile = open(outfile, 'w')
        raw = self.doc.toxml()
        try:
            raw = raw.encode('utf-8')
        except:
            print 'warning: could not encode to unicode'

        outfile.write(raw)
        outfile.close()

    # Don't blame me if you don't have a command-line shortcut to
    # simply the best free browser of the world.
    def preview(self):
        self.write('tmp.svg')
        from subprocess import call
        call(["firefox", "tmp.svg"])

    def tostring(self):
        return self.doc.toxml()

    # This is an artifact of an older version of Kartograph, but
    # maybe we'll need it later. It will load an SVG document from
    # a file.
    @staticmethod
    def load(filename):
        svg = SvgDocument()
        dom = parse(filename)
        svg.doc = dom
        svg.root = dom.getElementsByTagName('svg')[0]
        return svg


def _add_attrs(node, attrs):
    for key in attrs:
        node.setAttribute(key, str(attrs[key]))
