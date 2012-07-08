
from layersource import LayerSource
from kartograph.errors import *
from kartograph.geometry import BBox, create_feature

verbose = False


class OpenStreetMapLayer(LayerSource):
    """
    this class handles shapefile layers
    """

    def __init__(self, src, osm_query='1', osm_type='polygon'):
        """
        initialize shapefile reader
        """
        import psycopg2
        self.conn = psycopg2.connect(src)
        self.type = osm_type
        self.query = osm_query
        self.load_feature_meta()

    def load_feature_meta(self):
        print "reading from postgis database"
        cur = self.conn.cursor()
        # At first we find out what properties are available
        fields = []
        cur.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'planet_osm_%s';" % self.type)
        for rec in cur:
            if rec[0] not in ('way', 'z_order'):
                fields.append(rec[0])

        cur.execute('SELECT "%s" FROM planet_osm_%s WHERE %s' % ('", "'.join(fields), self.type, self.query))
        for rec in cur:
            meta = {}
            for f in range(len(fields)):
                if rec[f]:
                    meta[fields[f]] = rec[f]
            print meta

    def get_features(self, filter=None, bbox=None, verbose=False, ignore_holes=False, min_area=False, charset='utf-8'):
        """
        ### Get features
        """
        res = []
        # We will try these encodings..
        try_encodings = ('utf-8', 'latin-1', 'iso-8859-2')
        tried_encodings = [charset]
        # Eventually we convert the bbox list into a proper BBox instance
        if bbox is not None and not isinstance(bbox, BBox):
            bbox = BBox(bbox[2] - bbox[0], bbox[3] - bbox[1], bbox[0], bbox[1])
        ignored = 0
        for i in range(0, len(self.recs)):
            # Read all record attributes
            drec = {}
            for j in range(len(self.attributes)):
                drec[self.attributes[j]] = self.recs[i][j]
            # For each record that is not filtered..
            if filter is None or filter(drec):
                props = {}
                # ..we try to decode the attributes (shapefile charsets are arbitrary)
                for j in range(len(self.attributes)):
                    val = self.recs[i][j]
                    if isinstance(val, str):
                        try:
                            val = val.decode(charset)
                        except:
                            if verbose:
                                print 'warning: could not decode "%s" to %s' % (val, charset)
                            next_guess = False
                            for enc in try_encodings:
                                if enc not in tried_encodings:
                                    next_guess = enc
                                    tried_encodings.append(enc)
                                    break
                            if next_guess:
                                if verbose:
                                    print 'trying %s now..' % next_guess
                                charset = next_guess
                                j -= 1
                                continue
                            else:
                                raise KartographError('having problems to decode the input data "%s"' % val)
                    if isinstance(val, (str, unicode)):
                        val = val.strip()
                    props[self.attributes[j]] = val

                # Read the shape from the shapefile (can take some time..)..
                shp = self.get_shape(i)

                # ..and convert the raw shape into a shapely.geometry
                geom = shape2geometry(shp, ignore_holes=ignore_holes, min_area=min_area, bbox=bbox)
                if geom is None:
                    ignored += 1
                    continue

                # Finally we construct the map feature and append it to the
                # result list
                feature = create_feature(geom, props)
                res.append(feature)
        if bbox is not None and ignored > 0 and verbose:
            print "-ignoring %d shapes (not in bounds %s )" % (ignored, bbox)
        return res

# # shape2geometry


def shape2geometry(shp, ignore_holes=False, min_area=False, bbox=False):
    if bbox:
        sbbox = BBox(left=shp.bbox[0], top=shp.bbox[1], width=shp.bbox[2] - shp.bbox[0], height=shp.bbox[3] - shp.bbox[1])
        if not bbox.intersects(sbbox):
            # ignore the shape if it's not within the bbox
            return None

    if shp.shapeType in (5, 15):  # multi-polygon
        geom = shape2polygon(shp, ignore_holes=ignore_holes, min_area=min_area)
    elif shp.shapeType == 3:  # line
        geom = points2line(shp)
    else:
        raise KartographError('unknown shape type (%d) in shapefile %s' % (shp.shapeType, self.shpSrc))
    return geom


def shape2polygon(shp, ignore_holes=False, min_area=False):
    """
    converts a shapefile polygon to geometry.MultiPolygon
    """
    # from kartograph.geometry import MultiPolygon
    from shapely.geometry import Polygon, MultiPolygon
    from kartograph.geometry.utils import is_clockwise
    parts = shp.parts[:]
    parts.append(len(shp.points))
    exteriors = []
    holes = []
    for j in range(len(parts) - 1):
        pts = shp.points[parts[j]:parts[j + 1]]
        if shp.shapeType == 15:
            # remove z-coordinate from PolygonZ contours (not supported)
            for k in range(len(pts)):
                pts[k] = pts[k][:2]
        cw = is_clockwise(pts)
        if cw:
            exteriors.append(pts)
        else:
            holes.append(pts)
    if ignore_holes:
        holes = None
    if len(exteriors) == 1:
        poly = Polygon(exteriors[0], holes)
    elif len(exteriors) > 1:
        # use multipolygon, but we need to assign the holes to the right
        # exteriors
        from kartograph.geometry import BBox
        used_holes = set()
        polygons = []
        for ext in exteriors:
            bbox = BBox()
            my_holes = []
            for pt in ext:
                bbox.update(pt)
            for h in range(len(holes)):
                if h not in used_holes:
                    hole = holes[h]
                    if bbox.check_point(hole[0]):
                        # this is a very weak test but it should be sufficient
                        used_holes.add(h)
                        my_holes.append(hole)
            polygons.append(Polygon(ext, my_holes))
        if min_area:
            # compute maximum area
            max_area = 0
            for poly in polygons:
                max_area = max(max_area, poly.area)
            # filter out polygons that are below min_area * max_area
            polygons = [poly for poly in polygons if poly.area >= min_area * max_area]
        poly = MultiPolygon(polygons)
    else:
        raise KartographError('shapefile import failed - no outer polygon found')
    return poly


def points2line(shp):
    """ converts a shapefile line to geometry.Line """
    from kartograph.geometry import PolyLine
    parts = shp.parts[:]
    parts.append(len(shp.points))
    lines = []
    for j in range(len(parts) - 1):
        pts = shp.points[parts[j]:parts[j + 1]]
        lines.append(pts)
    return PolyLine(lines)
