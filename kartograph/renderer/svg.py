
from kartograph.renderer import MapRenderer
from kartograph.errors import KartographError
from kartograph.mapstyle import style_diff, remove_unit

# This script contains everything that is needed by Kartograph to finally
# render the processed maps into SVG files.
#

# The SVG renderer is based on xml.dom.minidom.
from xml.dom import minidom
from xml.dom.minidom import parse
import re


class SvgRenderer(MapRenderer):

    def render(self, style, pretty_print=False):
        """
        The render() method prepares a new empty SVG document and
        stores all the layer features into SVG groups.
        """
        self.style = style
        self.pretty_print = pretty_print
        self._init_svg_doc()
        self._store_layers_to_svg()
        if self.map.options['export']['scalebar'] != False:
            self._render_scale_bar(self.map.options['export']['scalebar'])

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
            style='stroke-linejoin: round; stroke:#000; fill: none;',
            pretty_print=self.pretty_print)

        defs = svg.node('defs', svg.root)
        style = svg.node('style', defs, type='text/css')
        css = 'path { fill-rule: evenodd; }'
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
        self.svg = svg

    def _render_feature(self, feature, attributes=[], labelOpts=False):
        node = self._render_geometry(feature.geometry)
        if node is None:
            return None

        if attributes == 'all':
            attributes = []
            for k in feature.props:
                attributes.append(dict(src=k, tgt=k))

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

        return node

    def _render_geometry(self, geometry):
        from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point
        if geometry is None:
            return
        if isinstance(geometry, (Polygon, MultiPolygon)):
            return self._render_polygon(geometry)
        elif isinstance(geometry, (LineString, MultiLineString)):
            return self._render_line(geometry)
        elif isinstance(geometry, (Point)):
            return self._render_point(geometry)
        else:
            raise KartographError('svg renderer doesn\'t know how to handle ' + str(type(geometry)))

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

    def _render_line(self, geometry):
        """ constructs a svg representation of this line """
        _round = self.map.options['export']['round']
        path_str = ""
        if _round is False:
            fmt = '%f,%f'
        else:
            fmt = '%.' + str(_round) + 'f'
            fmt = fmt + ',' + fmt

        geoms = hasattr(geometry, 'geoms') and geometry.geoms or [geometry]
        for line in geoms:
            if line is None:
                continue
            cont_str = ""
            kept = []
            for pt in line.coords:
                kept.append(pt)
            for pt in kept:
                if cont_str == "":
                    cont_str = "M"
                else:
                    cont_str += "L"
                cont_str += fmt % pt
            cont_str += " "
            if kept[0] == kept[-1]:
                cont_str += "Z "
            path_str += cont_str
        if path_str == "":
            return None
        path = self.svg.node('path', d=path_str)
        return path

    def _store_layers_to_svg(self):
        """
        store features in svg
        """
        svg = self.svg
        # label_groups = []
        for layer in self.map.layers:
            if len(layer.features) == 0:
                # print "ignoring empty layer", layer.id
                continue  # ignore empty layers
            if layer.options['render']:
                g = svg.node('g', svg.root, id=layer.id)
                g.setAttribute('class', ' '.join(layer.classes))
                layer_css = self.style.applyStyle(g, layer.id, layer.classes)

            # Create an svg group for labels of this layer
            lbl = layer.options['labeling']
            if lbl is not False:
                if lbl['buffer'] is not False:
                    lgbuf = svg.node('g', svg.root, id=layer.id + '-label-buffer')
                    self.style.applyStyle(lgbuf, layer.id + '-label', ['label'])
                    self.style.applyStyle(lgbuf, layer.id + '-label-buffer', ['label-buffer'])
                    _apply_default_label_styles(lgbuf)
                    lbl['lg-buffer'] = lgbuf
                lg = svg.node('g', svg.root, id=layer.id + '-label', stroke='none')
                self.style.applyStyle(lg, layer.id + '-label', ['label'])
                _apply_default_label_styles(lg)
                lbl['lg'] = lg
            else:
                lg = None

            for feat in layer.features:
                if layer.options['render']:
                    node = self._render_feature(feat, layer.options['attributes'])
                    if node is not None:
                        feat_css = self.style.getStyle(layer.id, layer.classes, feat.props)
                        feat_css = style_diff(feat_css, layer_css)
                        for prop in feat_css:
                            node.setAttribute(prop, str(feat_css[prop]))
                        g.appendChild(node)
                    else:
                        pass
                        #sys.stderr.write("feature.to_svg is None", feat)
                if lbl is not False:
                    self._render_label(layer, feat, lbl)

        # Finally add label groups on top of all other groups
        # for lg in label_groups:
        #    svg.root.appendChild(lg)

    def _render_point(self, geometry):
        dot = self.svg.node('circle', cx=geometry.x, cy=geometry.y, r=2)
        return dot

    def _render_label(self, layer, feature, labelOpts):
        #if feature.geometry.area < 20:
        #    return
        try:
            cx, cy = _get_label_position(feature.geometry, labelOpts['position'])
        except KartographError:
            return

        key = labelOpts['key']
        if not key:
            key = feature.props.keys()[0]
        if key not in feature.props:
            #sys.stderr.write('could not find feature property "%s" for labeling\n' % key)
            return
        if 'min-area' in labelOpts and feature.geometry.area < float(labelOpts['min-area']):
            return
        text = feature.props[key]
        if labelOpts['buffer'] is not False:
            l = self._label(text, cx, cy, labelOpts['lg-buffer'], labelOpts)
            self.style.applyFeatureStyle(l, layer.id + '-label', ['label'], feature.props)
            self.style.applyFeatureStyle(l, layer.id + '-label-buffer', ['label-buffer'], feature.props)
        l = self._label(text, cx, cy, labelOpts['lg'], labelOpts)
        self.style.applyFeatureStyle(l, layer.id + '-label', ['label'], feature.props)

    def _label(self, text, x, y, group, opts):
        # split text into ines
        if 'split-chars' not in opts:
            lines = [text]
        else:
            if 'split-at' not in opts:
                opts['split-at'] = 10
            lines = split_at(text, opts['split-chars'], opts['split-at'])
        lh = remove_unit(group.getAttribute('font-size'))
        if lh is None:
            lh = 12
        line_height = remove_unit(group.getAttribute('line-height'))
        if line_height:
            lh = line_height
        h = len(lines) * lh
        lbl = self.svg.node('text', group, y=y - h * 0.5, text__anchor='middle')
        yo = 0
        for line in lines:
            tspan = self.svg.node('tspan', lbl, x=x, dy=yo)
            yo += lh
            self.svg.cdata(line, tspan)
        return lbl

    def _render_scale_bar(self, opts):

        def format(m):
            if m > 1000:
                if m % 1000 == 0:
                    return (str(int(m / 1000)), 'km')
                else:
                    return (str(round(m / 1000, 1)), 'km')
            return (str(m), 'm')

        svg = self.svg
        meters, pixel = self.map.scale_bar_width()
        if 'align' not in opts:
            opts['align'] = 'bl'  # default to bottom left
        if 'offset' not in opts:
            opts['offset'] = 20  # 20px offset
        g = svg.node('g', svg.root, id='scalebar', shape__rendering='crispEdges',  text__anchor='middle', stroke='none', fill='#000', font__size=13)
        left = (opts['offset'], self.map.view.width - pixel - opts['offset'])[opts['align'][1] != 'l']
        top = (opts['offset'] + 20, self.map.view.height - opts['offset'])[opts['align'][0] != 't']
        dy = -8
        paths = []
        paths.append((left, top + dy, left, top, left + pixel, top, left + pixel, top + dy))
        for i in (1.25, 2.5, 3.75, 5, 6.25, 7.5, 8.75):
            _dy = dy
            if i != 5:
                _dy *= 0.5
            paths.append((left + pixel * i / 10.0, top + dy, left + pixel * i / 10.0, top))

        def path(pts, stroke, strokeWidth):
            d = ('M%d,%d' + ('L%d,%d' * (len(pts[2:]) / 2))) % pts
            svg.node('path', g, d=d, fill='none', stroke=stroke, stroke__width=strokeWidth)

        for pts in paths:
            path(pts, '#fff', 5)
        for pts in paths:
            path(pts, '#000', 1)

        def lbl(txt, x=0, y=0):
            # buffer
            lbl = svg.node('text', g, x=x, y=y, stroke='#fff', stroke__width='4px')
            svg.cdata(txt, lbl)
            self.style.applyStyle(lbl, 'scalebar', [])
            self.style.applyStyle(lbl, 'scalebar-buffer', [])
            # text
            lbl = svg.node('text', g, x=x, y=y)
            svg.cdata(txt, lbl)
            self.style.applyStyle(lbl, 'scalebar', [])

        lbl('%s%s' % format(meters), x=int(left + pixel), y=(top + dy - 7))
        lbl('%s' % format(meters * 0.5)[0], x=int(left + pixel * 0.5), y=(top + dy - 7))
        lbl('%s' % format(meters * 0.25)[0], x=int(left + pixel * 0.25), y=(top + dy - 7))
        lbl('0', x=int(left), y=(top + dy - 7))

    def write(self, filename):
        self.svg.write(filename, self.pretty_print)

    def preview(self, command):
        self.svg.preview(command, self.pretty_print)

    def __str__(self):
        return self.svg.tostring(self.pretty_print)


def split_at(text, chars, minLen):
    res = [text]
    for char in chars:
        tmp = []
        for text in res:
            parts = text.split(char)
            for p in range(len(parts) - 1):
                if char != '(':
                    parts[p] += char
                else:
                    parts[p + 1] = char + parts[p + 1]
            tmp += parts
        res = tmp
    o = []
    keep = ''
    for token in res:
        if len(keep) > minLen:
            o.append(keep)
            keep = ''
        keep += token
    o.append(keep)
    return o

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
    def write(self, outfile, pretty_print=False):
        if isinstance(outfile, (str, unicode)):
            outfile = open(outfile, 'w')
        if pretty_print:
            raw = self.doc.toprettyxml('utf-8')
        else:
            raw = self.doc.toxml('utf-8')
        try:
            raw = raw.encode('utf-8')
        except:
            print 'warning: could not encode to unicode'

        outfile.write(raw)
        outfile.close()

    # Don't blame me if you don't have a command-line shortcut to
    # simply the best free browser of the world.
    def preview(self, command, pretty_print=False):
        import tempfile
        tmpfile = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
        self.write(tmpfile, pretty_print)
        print 'map stored to', tmpfile.name
        from subprocess import call
        call([command, tmpfile.name])

    def tostring(self, pretty_print=False):
        if pretty_print:
            return self.doc.toprettyxml()
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
        node.setAttribute(key.replace('__', '-'), str(attrs[key]))


def _get_label_position(geometry, pos):
    if pos == 'centroid' and not (geometry is None):
        pt = geometry.centroid
        return (pt.x, pt.y)
    else:
        raise KartographError('unknown label positioning mode ' + pos)


def _apply_default_label_styles(lg):
    if not lg.getAttribute('font-size'):
        lg.setAttribute('font-size', '12px')
    if not lg.getAttribute('font-family'):
        lg.setAttribute('font-family', 'Arial')
    if not lg.getAttribute('fill'):
        lg.setAttribute('fill', '#000')
