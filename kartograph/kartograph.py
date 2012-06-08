
from options import parse_options
from layersource import handle_layer_source
from geometry import BBox, View
from geometry.utils import geom_to_bbox
from shapely.geometry.base import BaseGeometry
from shapely.geometry import Polygon, LineString, MultiPolygon
from proj import projections
from filter import filter_record
from errors import *
from copy import deepcopy
from renderer import SvgRenderer, KmlRenderer


_verbose = False

_known_renderer = {
    'svg': SvgRenderer,
    'kml': KmlRenderer
}


class Kartograph(object):
    """
    main class of Kartograph
    """
    def __init__(self):
        self.layerCache = {}
        pass

    def generate(self, opts, outfile=None, format='svg', preview=None, verbose=False):
        """
        generates svg map
        """
        if preview is None:
            preview = outfile is not None

        opts = deepcopy(opts)
        parse_options(opts)

        global _verbose
        _verbose = verbose

        _map = Map(opts, self.layerCache, format=format)

        format = format.lower()
        if format in _known_renderer:
            renderer = _known_renderer[format](_map)
            renderer.render()
            if outfile is None:
                if preview:
                    renderer.preview()
                else:
                    return renderer
            else:
                if preview:
                    renderer.preview()
                renderer.write(outfile)
        else:
            raise KartographError('unknown format: %s' % format)


class Map(object):

    def __init__(me, options, layerCache, verbose=False, format='svg', src_encoding=None):
        me.options = options
        me._verbose = verbose
        me.format = format
        me.layers = []
        me.layersById = {}
        me._bounds_polygons_cache = False
        me._unprojected_bounds = None
        if not src_encoding:
            src_encoding = 'utf-8'
        me._source_encoding = src_encoding

        for layer_cfg in options['layers']:
            layer_id = layer_cfg['id']
            layer = MapLayer(layer_id, layer_cfg, me, layerCache)
            me.layers.append(layer)
            me.layersById[layer_id] = layer

        me.proj = me._init_projection()
        me.bounds_poly = me._init_bounds()
        me.view = me._get_view()
        me.view_poly = me._init_view_poly()

        # get features
        for layer in me.layers:
            layer.get_features()

        #_debug_show_features(layerFeatures[id], 'original')
        me._join_layers()
        #_debug_show_features(layerFeatures[id], 'joined')
        if options['export']['crop-to-view'] and format != 'kml':
            me._crop_layers_to_view()
        #_debug_show_features(layerFeatures[id], 'cropped to view')
        me._simplify_layers()
        #_debug_show_features(layerFeatures[id], 'simplified')
        #self.crop_layers(layers, layerOpts, layerFeatures)
        me._subtract_layers()

    def _init_projection(self):
        """
        instantiates the map projection
        """
        if self.format in ('kml', 'json'):
            return projections['ll']()  # use no projection for KML

        map_center = self.__get_map_center()
        opts = self.options
        projC = projections[opts['proj']['id']]
        p_opts = {}
        for prop in opts['proj']:
            if prop != "id":
                p_opts[prop] = opts['proj'][prop]
            if prop == "lon0" and p_opts[prop] == "auto":
                p_opts[prop] = map_center[0]
            elif prop == "lat0" and p_opts[prop] == "auto":
                p_opts[prop] = map_center[1]
        return projC(**p_opts)

    def __get_map_center(self):
        """
        used by _init_projection() to determine the center of the
        map projection, depending on the bounds config
        """
        opts = self.options
        mode = opts['bounds']['mode']
        data = opts['bounds']['data']

        lon0 = 0

        if mode == 'bbox':
            lon0 = data[0] + 0.5 * (data[2] - data[0])
            lat0 = data[1] + 0.5 * (data[3] - data[1])

        elif mode[:5] == 'point':
            lon0 = 0
            lat0 = 0
            m = 1 / len(data)
            for (lon, lat) in data:
                lon0 += m * lon
                lat0 += m * lat

        elif mode[:4] == 'poly':
            features = self._get_bounds_polygons()
            if len(features) > 0:
                if isinstance(features[0].geom, BaseGeometry):
                    (lon0, lat0) = features[0].geom.representative_point().coords[0]
            else:
                lon0 = 0
                lat0 = 0
        else:
            print "unrecognized bound mode", mode
        return (lon0, lat0)

    def _init_bounds(self):
        """
        computes the (x,y) bounding box for the map,
        given a specific projection
        """
        if self.format in ('kml', 'json'):
            return None  # no bounds needed for KML

        from geometry.utils import bbox_to_polygon, geom_to_bbox

        opts = self.options
        proj = self.proj
        bnds = opts['bounds']
        mode = bnds['mode'][:]
        data = bnds['data']

        if _verbose:
            print 'using bounds mode', mode

        if mode == "bbox":  # catch special case bbox
            sea = proj.bounding_geometry(data, projected=True)
            sbbox = geom_to_bbox(sea)
            sbbox.inflate(sbbox.width * bnds['padding'])
            return bbox_to_polygon(sbbox)

        bbox = BBox()

        if mode[:5] == "point":
            for lon, lat in data:
                pt = proj.project(lon, lat)
                bbox.update(pt)

        if mode[:4] == "poly":
            features = self._get_bounds_polygons()
            ubbox = BBox()
            if len(features) > 0:
                for feature in features:
                    ubbox.join(geom_to_bbox(feature.geometry))
                    feature.project(proj)
                    fbbox = geom_to_bbox(feature.geometry, data["min-area"])
                    bbox.join(fbbox)
                self._unprojected_bounds = ubbox
            else:
                raise KartographError('no features found for calculating the map bounds')
        bbox.inflate(bbox.width * bnds['padding'])
        return bbox_to_polygon(bbox)

    def _get_bounds_polygons(self):
        """
        for bounds mode "polygons" this helper function
        returns a list of all polygons that the map should
        be cropped to
        """
        if self._bounds_polygons_cache:
            return self._bounds_polygons_cache

        opts = self.options
        features = []
        data = opts['bounds']['data']
        id = data['layer']

        if id not in self.layersById:
            raise KartographError('layer not found "%s"' % id)
        layer = self.layersById[id]

        if layer.options['filter'] is False:
            layerFilter = lambda a: True
        else:
            layerFilter = lambda rec: filter_record(layer.options['filter'], rec)

        if data['filter']:
            boundsFilter = lambda rec: filter_record(data['filter'], rec)
        else:
            boundsFilter = lambda a: True

        filter = lambda rec: layerFilter(rec) and boundsFilter(rec)
        features = layer.source.get_features(filter=filter, min_area=data["min-area"], charset=layer.options['charset'])

        # remove features that are too small
        if layer.options['filter-islands']:
            features = [feature for feature in features if feature.geometry.area > layer.options['filter-islands']]

        self._bounds_polygons_cache = features
        return features

    def _get_view(self):
        """
        returns the output view
        """
        if self.format in ('kml', 'json'):
            return View()  # no view transformation needed for KML

        self.src_bbox = bbox = geom_to_bbox(self.bounds_poly)
        opts = self.options
        exp = opts["export"]
        w = exp["width"]
        h = exp["height"]
        ratio = exp["ratio"]

        if ratio == "auto":
            ratio = bbox.width / float(bbox.height)

        if h == "auto":
            h = w / ratio
        elif w == "auto":
            w = h * ratio
        return View(bbox, w, h - 1)

    def _init_view_poly(self):
        """
        creates a polygon that represents the rectangular view bounds
        used for cropping the geometries to not overlap the view
        """
        if self.format in ('kml', 'json'):
            return None  # no view polygon needed for KML
        w = self.view.width
        h = self.view.height
        return Polygon([(0, 0), (0, h), (w, h), (w, 0)])

    def _simplify_layers(self):
        """
        performs polygon simplification
        """
        from simplify import create_point_store, simplify_lines

        point_store = create_point_store()  # create a new empty point store

        # compute topology for all layers
        for layer in self.layers:
            if layer.options['simplify'] is not False:
                for feature in layer.features:
                    feature.compute_topology(point_store, layer.options['unify-precision'])

        # break features into lines
        for layer in self.layers:
            if layer.options['simplify'] is not False:
                for feature in layer.features:
                    feature.break_into_lines()

        # simplify lines
        total = 0
        kept = 0
        for layer in self.layers:
            if layer.options['simplify'] is not False:
                for feature in layer.features:
                    lines = feature.break_into_lines()
                    lines = simplify_lines(lines, layer.options['simplify']['method'], layer.options['simplify']['tolerance'])
                    for line in lines:
                        total += len(line)
                        for pt in line:
                            if not pt.deleted:
                                kept += 1
                    feature.restore_geometry(lines, layer.options['filter-islands'])
        return (total, kept)

    def _crop_layers_to_view(self):
        """
        cuts the layer features to the map view
        """
        for layer in self.layers:
            #out = []
            for feat in layer.features:
                if not feat.geometry.is_valid:
                    pass
                    #print feat.geometry
                    #_plot_geometry(feat.geometry)
                feat.crop_to(self.view_poly)
                #if not feat.is_empty():
                #    out.append(feat)
            #layer.features = out

    def _crop_layers(self):
        """
        handles crop-to
        """
        for layer in layers:
            if layer.options['crop-to'] is not False:
                cropped_features = []
                for tocrop in layer.features:
                    cbbox = geom_to_bbox(tocrop.geom)
                    crop_at_layer = layer.options['crop-to']
                    if crop_at_layer not in layers:
                        raise KartographError('you want to substract from layer "%s" which cannot be found' % crop_at_layer)
                    for crop_at in layerFeatures[crop_at_layer]:
                        if crop_at.geom.bbox().intersects(cbbox):
                            tocrop.crop_to(crop_at.geom)
                            cropped_features.append(tocrop)
                layer.features = cropped_features

    def _subtract_layers(self):
        """
        handles subtract-from
        """
        for layer in self.layers:
            if layer.options['subtract-from'] is not False:
                for feat in layer.features:
                    if feat.geom is None:
                        continue
                    cbbox = geom_to_bbox(feat.geom)
                    for subid in layer.options['subtract-from']:
                        if subid not in layers:
                            raise KartographError('you want to subtract from layer "%s" which cannot be found' % subid)
                        for sfeat in layerFeatures[subid]:
                            if sfeat.geom and geom_to_bbox(sfeat.geom).intersects(cbbox):
                                sfeat.subtract_geom(feat.geom)
                layer.features = []

    def _join_layers(self):
        """
        joins features in layers
        """
        from geometry.utils import join_features

        for layer in self.layers:
            if layer.options['join'] is not False:
                unjoined = 0
                join = layer.options['join']
                groupBy = join['group-by']
                groups = join['groups']
                if not groups:
                    # auto populate groups
                    groups = {}
                    for feat in layer.features:
                        fid = feat.props[groupBy]
                        groups[fid] = [fid]

                groupAs = join['group-as']
                groupFeatures = {}
                res = []
                for feat in layer.features:
                    found_in_group = False
                    for g_id in groups:
                        if g_id not in groupFeatures:
                            groupFeatures[g_id] = []
                        if feat.props[groupBy] in groups[g_id] or str(feat.props[groupBy]) in groups[g_id]:
                            groupFeatures[g_id].append(feat)
                            found_in_group = True
                            break
                    if not found_in_group:
                        unjoined += 1
                        res.append(feat)
                #print unjoined,'features were not joined'
                for g_id in groups:
                    props = {}
                    for feat in groupFeatures[g_id]:
                        fprops = feat.props
                        for key in fprops:
                            if key not in props:
                                props[key] = fprops[key]
                            else:
                                if props[key] != fprops[key]:
                                    props[key] = "---"

                    if groupAs is not False:
                        props[groupAs] = g_id
                    if g_id in groupFeatures:
                        res += join_features(groupFeatures[g_id], props)
                layer.features = res


class MapLayer(object):

    def __init__(self, id, options, _map, cache):
        self.id = id
        self.options = options
        self.map = _map
        self.cache = cache
        self._prepare_layer()

    def _prepare_layer(self):
        """
        prepares layer sources
        """
        while self.id in self.map.layersById:
            self.id += "_"  # make layer id unique
        self.source = handle_layer_source(self.options, self.cache)

    def get_features(layer, filter=False, min_area=0):
        """
        returns a list of projected and filtered features of a layer
        """
        opts = layer.map.options
        is_projected = False

        bbox = [-180, -90, 180, 90]
        if opts['bounds']['mode'] == "bbox":
            bbox = opts['bounds']['data']
        if 'crop' in opts['bounds'] and opts['bounds']['crop']:
            if opts['bounds']['crop'] == "auto":
                if layer.map._unprojected_bounds:
                    bbox = layer.map._unprojected_bounds
                    bbox.inflate(inflate=opts['bounds']['padding'] * 2)
                else:
                    print 'could not compute bounding box for auto-cropping'
            else:
                bbox = opts['bounds']['crop']

        if 'src' in layer.options:  # regular geodata layer
            if layer.options['filter'] is False:
                filter = None
            else:
                filter = lambda rec: filter_record(layer.options['filter'], rec)

            features = layer.source.get_features(
                filter=filter,
                bbox=bbox,
                ignore_holes='ignore-holes' in layer.options and layer.options['ignore-holes'],
                charset=layer.options['charset']
            )
            if _verbose:
                print 'loaded %d features from shapefile %s' % (len(features), layer.options['src'])

        elif 'special' in layer.options:  # special layers need special treatment
            if layer.options['special'] == "graticule":
                lats = layer.options['latitudes']
                lons = layer.options['longitudes']
                features = layer.source.get_features(lats, lons, self.map.proj, bbox=bbox)

            elif layer.options['special'] == "sea":
                features = layer.source.get_features(self.map.proj)
                is_projected = True

        for feature in features:
            if not is_projected:
                feature.project(layer.map.proj)
            feature.project_view(layer.map.view)

        # remove features that don't intersect our view polygon
        if layer.map.view_poly:
            features = [feature for feature in features if feature.geometry and feature.geometry.intersects(layer.map.view_poly)]
        layer.features = features


def _plot_geometry(geom, fill='#ffcccc', stroke='#333333', alpha=1, msg=None):
    from matplotlib import pyplot
    from matplotlib.figure import SubplotParams
    from descartes import PolygonPatch

    if isinstance(geom, (Polygon, MultiPolygon)):
        b = geom.bounds
        # b = (min(c[0], b[0]), min(c[1], b[1]), max(c[2], b[2]), max(c[3], b[3]))
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
    #ax.xaxis.set_visible(False)
    #ax.yaxis.set_visible(False)
    #ax.set_frame_on(False)
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

        #ob = LineString(filtered)
        #x, y = ob.xy
        #ax.plot(x, y, '-', color='#dd4444', linewidth=1, alpha=0.5, solid_capstyle='round', zorder=1)
        #ax.plot(x[0], y[0], 'o', color='#cc0000', zorder=3)
        #ax.plot(x[-1], y[-1], 'o', color='#cc0000', zorder=3)

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
    """ for debugging purposes we're going to output the features """
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
