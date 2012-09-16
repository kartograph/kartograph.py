
from layersource import handle_layer_source
from filter import filter_record


_verbose = False


class MapLayer(object):

    """
    MapLayer
    --------

    Represents a layer in the map which contains a list of map features
    """

    def __init__(self, id, options, _map, cache):
        # Store layer properties as instance properties
        self.id = id
        self.options = options
        self.map = _map
        self.cache = cache
        if 'class' not in options:
            self.classes = []
        elif isinstance(options['class'], basestring):
            self.classes = options['class'].split(' ')
        elif isinstance(options['class'], list):
            self.classes = options['class']
        # Make sure that the layer id is unique within the map.
        while self.id in self.map.layersById:
            self.id += "_"
        # Instantiate the layer source which will generate features from the source
        # geo data such as shapefiles or virtual sources such as graticule lines.
        self.source = handle_layer_source(self.options, self.cache)

    def get_features(layer, filter=False, min_area=0):
        """
        ### get_features()
        Returns a list of projected and filtered features of a layer.
        """
        opts = layer.map.options
        is_projected = False

        # Let's see if theres a better bounding box than this..
        bbox = [-180, -90, 180, 90]

        # Use the clipping mode defined in the map configuration
        if opts['bounds']['mode'] == "bbox":
            bbox = opts['bounds']['data']
        # The 'crop' property overrides the clipping settings
        if 'crop' in opts['bounds'] and opts['bounds']['crop']:
            # If crop is set to "auto", which is the default behaviour, Kartograph
            # will use the actual bounding geometry to compute the bounding box
            if opts['bounds']['crop'] == "auto":
                if layer.map._unprojected_bounds:
                    bbox = layer.map._unprojected_bounds
                    bbox.inflate(inflate=opts['bounds']['padding'] * 2)
                elif _verbose:
                    pass
                    #print 'could not compute bounding box for auto-cropping'
            else:
                # otherwise it will use the user defined bbox in the format
                # [minLon, minLat, maxLon, maxLat]
                bbox = opts['bounds']['crop']

        # If the layer has the "src" property, it is a **regular map layer** source, which
        # means that there's an exernal file that we load the geometry and meta data from.
        if 'src' in layer.options:
            if layer.options['filter'] is False:
                filter = None
            else:
                filter = lambda rec: filter_record(layer.options['filter'], rec)

            # Now we ask the layer source to generate the features that will be displayed
            # in the map.
            features = layer.source.get_features(
                filter=filter,
                bbox=bbox,
                ignore_holes='ignore-holes' in layer.options and layer.options['ignore-holes'],
                charset=layer.options['charset']
            )
            if _verbose:
                #print 'loaded %d features from shapefile %s' % (len(features), layer.options['src'])
                pass

        # In contrast to regular layers, the geometry for **special (or virtual) layers** is generated
        # by Kartograph itself, based on some properties defined in the layer config.
        elif 'special' in layer.options:
            # The graticule layer generates line features for longitudes and latitudes
            if layer.options['special'] == "graticule":
                lats = layer.options['latitudes']
                lons = layer.options['longitudes']
                features = layer.source.get_features(lats, lons, layer.map.proj, bbox=bbox)

            # The "sea" layer generates a MultiPolygon that represents the entire boundary
            # of the map. Especially useful for non-cylindrical map projections.
            elif layer.options['special'] == "sea":
                features = layer.source.get_features(layer.map.proj)
                is_projected = True

        for feature in features:
            # If the features are not projected yet, we project them now.
            if not is_projected:
                feature.project(layer.map.proj)
            # Transform features to view coordinates.
            feature.project_view(layer.map.view)

        # Remove features that don't intersect our clipping polygon
        if layer.map.view_poly:
            features = [feature for feature in features
            if feature.geometry and feature.geometry.intersects(layer.map.view_poly)]
        layer.features = features
