
from layersource import LayerSource
from kartograph.errors import *
from kartograph.geometry import BBox, create_feature
from os.path import exists
from osgeo.osr import SpatialReference
import pyproj
import shapefile


verbose = False


class ShapefileLayer(LayerSource):
    """
    this class handles shapefile layers
    """

    def __init__(self, src):
        """
        initialize shapefile reader
        """
        if isinstance(src, unicode):
            src = src.encode('ascii', 'ignore')
        src = self.find_source(src)
        self.shpSrc = src
        self.sr = shapefile.Reader(src)
        self.recs = []
        self.shapes = {}
        self.load_records()
        self.proj = None
        # Check if there's a spatial reference
        prj_src = src[:-4] + '.prj'
        if exists(prj_src):
            prj_text = open(prj_src).read()
            srs = SpatialReference()
            if srs.ImportFromWkt(prj_text):
                raise ValueError("Error importing PRJ information from: %s" % prj_file)
            if srs.IsProjected():
                self.proj = pyproj.Proj(srs.ExportToProj4())
                #print srs.ExportToProj4()

    def load_records(self):
        """
        ### Load records
        Load shapefile records into memory (but not the shapes).
        """
        self.recs = self.sr.records()
        self.attributes = []
        for a in self.sr.fields[1:]:
            self.attributes.append(a[0])
        i = 0
        self.attrIndex = {}
        for attr in self.attributes:
            self.attrIndex[attr] = i
            i += 1

    def get_shape(self, i):
        """
        ### Get shape
        Returns a shape of this shapefile. If the shape is requested for the first time,
        it will be loaded from the shapefile. Otherwise it will loaded from cache.
        """
        if i in self.shapes:  # check cache
            shp = self.shapes[i]
        else:  # load shape from shapefile
            shp = self.shapes[i] = self.sr.shapeRecord(i).shape
        return shp


    def forget_shape(self, i):
        if i in self.shapes:
            self.shapes.pop(i)

    def get_features(self, attr=None, filter=None, bbox=None, ignore_holes=False, min_area=False, charset='utf-8'):
        """
        ### Get features
        """
        res = []
        # We will try these encodings..
        known_encodings = ['utf-8', 'latin-1', 'iso-8859-2', 'iso-8859-15']
        try_encodings = [charset]
        for enc in known_encodings:
            if enc != charset:
                try_encodings.append(enc)
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
                    decoded = False
                    if isinstance(val, str):
                        for enc in try_encodings:
                            try:
                                val = val.decode(enc)
                                decoded = True
                                break
                            except:
                                if verbose:
                                    print 'warning: could not decode "%s" to %s' % (val, enc)
                        if not decoded:
                            raise KartographError('having problems to decode the input data "%s"' % val)
                    if isinstance(val, (str, unicode)):
                        val = val.strip()
                    props[self.attributes[j]] = val

                # Read the shape from the shapefile (can take some time..)..
                shp = self.get_shape(i)

                # ..and convert the raw shape into a shapely.geometry
                geom = shape2geometry(shp, ignore_holes=ignore_holes, min_area=min_area, bbox=bbox, proj=self.proj)
                if geom is None:
                    ignored += 1
                    self.forget_shape(i)
                    continue

                # Finally we construct the map feature and append it to the
                # result list
                feature = create_feature(geom, props)
                res.append(feature)
        if bbox is not None and ignored > 0 and verbose:
            print "-ignoring %d shapes (not in bounds %s )" % (ignored, bbox)
        return res

# # shape2geometry


def shape2geometry(shp, ignore_holes=False, min_area=False, bbox=False, proj=None):
    if shp is None:
        return None
    if bbox and shp.shapeType != 1:
        if proj:
            left, top = proj(shp.bbox[0], shp.bbox[1], inverse=True)
            right, btm = proj(shp.bbox[2], shp.bbox[3], inverse=True)
        else:
            left, top, right, btm = shp.bbox
        sbbox = BBox(left=left, top=top, width=right - left, height=btm - top)
        if not bbox.intersects(sbbox):
            # ignore the shape if it's not within the bbox
            return None

    if shp.shapeType in (5, 15):  # multi-polygon
        geom = shape2polygon(shp, ignore_holes=ignore_holes, min_area=min_area, proj=proj)
    elif shp.shapeType in (3, 13):  # line
        geom = shape2line(shp, proj=proj)
    elif shp.shapeType == 1: # point
        geom = shape2point(shp, proj=proj)
    else:
        raise KartographError('unknown shape type (%d)' % shp.shapeType)
    return geom


def shape2polygon(shp, ignore_holes=False, min_area=False, proj=None):
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
        if proj:
            project_coords(pts, proj)
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


def shape2line(shp, proj=None):
    """ converts a shapefile line to geometry.Line """
    from shapely.geometry import LineString, MultiLineString

    parts = shp.parts[:]
    parts.append(len(shp.points))
    lines = []
    for j in range(len(parts) - 1):
        pts = shp.points[parts[j]:parts[j + 1]]
        if shp.shapeType == 13:
            # remove z-coordinate from PolylineZ contours (not supported)
            for k in range(len(pts)):
                pts[k] = pts[k][:2]
        if proj:
            project_coords(pts, proj)
        lines.append(pts)
    if len(lines) == 1:
        return LineString(lines[0])
    elif len(lines) > 1:
        return MultiLineString(lines)
    else:
        raise KartographError('shapefile import failed - no line found')

def shape2point(shp, proj=None):
    from shapely.geometry import MultiPoint, Point
    points = shp.points[:]
    if len(points) == 1:
        return Point(points[0])
    elif len(points) > 1:
        return MultiPoint(points)
    else:
        raise KartographError('shapefile import failed - no points found')
    
  
def project_coords(pts, proj):
    for i in range(len(pts)):
        x, y = proj(pts[i][0], pts[i][1], inverse=True)
        pts[i][0] = x
        pts[i][1] = y
