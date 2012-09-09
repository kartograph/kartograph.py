
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, MultiPoint, Point
from kartograph.errors import KartographError


# # View

# Simple 2D coordinate transformation.

class View(object):
    """
    translates a point to a view
    """
    def __init__(self, bbox=None, width=None, height=None, padding=0):
        self.bbox = bbox
        self.width = width
        self.padding = padding
        self.height = height
        if bbox:
            self.scale = min((width - padding * 2) / bbox.width, (height - padding * 2) / bbox.height)

    def project(self, pt):
        bbox = self.bbox
        if not bbox:
            return pt
        s = self.scale
        h = self.height
        w = self.width
        px = pt[0]
        py = pt[1]
        x = (px - bbox.left) * s + (w - bbox.width * s) * .5
        y = (py - bbox.top) * s + (h - bbox.height * s) * .5
        return ((x, y), Point(x, y))[isinstance(pt, Point)]

    def project_inverse(self, pt):
        bbox = self.bbox
        if not bbox:
            return pt
        s = self.scale
        h = self.height
        w = self.width
        x = pt[0]
        y = pt[1]
        px = (x - (w - bbox.width * s) * .5) / s + bbox.left
        py = (y - (h - bbox.height * s) * .5) / s + bbox.top
        return ((px, py), Point(px, py))[isinstance(pt, Point)]

    def project_geometry(self, geometry):
        """ converts the given geometry to the view coordinates """
        geometries = hasattr(geometry, 'geoms') and geometry.geoms or [geometry]
        res = []

        # at first shift polygons
        #geometries = []
        #for geom in unshifted_geometries:
        #    geometries += self._shift_polygon(geom)

        for geom in geometries:
            if isinstance(geom, Polygon):
                res += self.project_polygon(geom)
            elif isinstance(geom, LineString):
                rings = self.project_linear_ring(geom)
                res += map(LineString, rings)
            elif isinstance(geom, Point):
                res.append(self.project((geom.x, geom.y)))
            else:
                raise KartographError('unknown geometry type %s' % geometry)

        if len(res) > 0:
            if isinstance(res[0], Polygon):
                if len(res) > 1:
                    return MultiPolygon(res)
                else:
                    return res[0]
            elif isinstance(res[0], LineString):
                if len(res) > 1:
                    return MultiLineString(res)
                else:
                    return LineString(res[0])
            else:
                if len(res) > 1:
                    return MultiPoint(res)
                else:
                    return Point(res[0])

    def project_polygon(self, polygon):
        ext = self.project_linear_ring(polygon.exterior)
        if len(ext) == 1:
            pts_int = []
            for interior in polygon.interiors:
                pts_int += self.project_linear_ring(interior)
            return [Polygon(ext[0], pts_int)]
        elif len(ext) == 0:
            return []
        else:
            raise KartographError('unhandled case: exterior is split into multiple rings')

    def project_linear_ring(self, ring):
        points = []
        for pt in ring.coords:
            x, y = self.project(pt)
            points.append((x, y))
        return [points]

    def __str__(self):
        return 'View(w=%f, h=%f, pad=%f, scale=%f, bbox=%s)' % (self.width, self.height, self.padding, self.scale, self.bbox)
