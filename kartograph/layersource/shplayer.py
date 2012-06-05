
from layersource import LayerSource
from os.path import basename
from kartograph.errors import *


class ShapefileLayer(LayerSource):
    """
    this class handles shapefile layers
    """

    def __init__(self, src):
        """
        initialize shapefile reader
        """
        import shapefile
        if isinstance(src, unicode):
            src = src.encode('ascii', 'ignore')
        self.shpSrc = src
        self.sr = shapefile.Reader(src)
        self.recs = []
        self.shapes = {}
        self.load_records()

    def load_records(self):
        """
        load shapefile records into memory. note that only the records are loaded and not the shapes.
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
        returns a shape of this shapefile. if requested for the first time, the shape is loaded from shapefile (slow)
        """
        if i in self.shapes:  # check cache
            shp = self.shapes[i]
        else:  # load shape from shapefile
            shp = self.shapes[i] = self.sr.shapeRecord(i).shape
        return shp

    def get_features(self, attr=None, filter=None, bbox=None, verbose=False, ignore_holes=False, min_area=False):
        """
        returns a list of features matching to the attr -> value pair
        """
        from kartograph.geometry import create_feature, BBox
        res = []
        if bbox is not None:
            bbox = BBox(bbox[2] - bbox[0], bbox[3] - bbox[1], bbox[0], bbox[1])
            ignored = 0
        for i in range(0, len(self.recs)):
            drec = {}
            for j in range(len(self.attributes)):
                drec[self.attributes[j]] = self.recs[i][j]
            if filter is None or filter(drec):
                props = {}
                for j in range(len(self.attributes)):
                    val = self.recs[i][j]
                    if isinstance(val, (str, unicode)):
                        val = val.strip()
                    props[self.attributes[j]] = val

                shp = self.get_shape(i)

                geom = shape2geometry(shp, ignore_holes=ignore_holes, min_area=min_area)

                #if bbox is not None and not bbox.intersects(geom.bbox()):
                #    ignored += 1
                #    continue  # ignore if not within bounds

                feature = create_feature(geom, props)
                res.append(feature)
        if bbox is not None and ignored > 0 and verbose:
            print "[%s] ignored %d shapes (not in bounds)" % (basename(self.shpSrc), ignored)
        return res


def shape2geometry(shp, ignore_holes=False, min_area=False):
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
