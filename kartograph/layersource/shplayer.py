
from layersource import LayerSource
from os.path import basename


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

    def get_features(self, attr=None, filter=None, bbox=None):
        """
        returns a list of features matching to the attr -> value pair
        """
        from kartograph.geometry import Feature, BBox
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

                if shp.shapeType == 5:  # multi-polygon
                    geom = points2polygon(shp)
                elif shp.shapeType == 3:  # line
                    geom = points2line(shp)
                else:
                    print 'unknown shape type', shp.shapeType

                if bbox is not None and not bbox.intersects(geom.bbox()):
                    ignored += 1
                    continue  # ignore if not within bounds

                feature = Feature(geom, props)
                res.append(feature)
        if bbox is not None:
            print "[%s] ignored %d shapes (not in bounds)" % (basename(self.shpSrc), ignored)
        return res


def points2polygon(shp):
    """
    converts a shapefile polygon to geometry.MultiPolygon
    """
    from kartograph.geometry import MultiPolygon
    parts = shp.parts[:]
    parts.append(len(shp.points))
    contours = []
    for j in range(len(parts) - 1):
        pts = shp.points[parts[j]:parts[j + 1]]
        pts_ = []
        lpt = None
        for pt in pts:
            if lpt is None:
                pts_.append(pt)
            elif pt != lpt:
                pts_.append(pt)
            lpt = pt
        contours.append(pts_)
    poly = MultiPolygon(contours)
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
