"""
    kartograph - a svg mapping library
    Copyright (C) 2011  Gregor Aisch

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import math
from kartograph.errors import KartographError
from shapely.geometry import Polygon, LineString, Point, MultiPolygon, MultiLineString, MultiPoint


class Proj(object):
    """
    base class for projections
    """
    HALFPI = math.pi * .5
    QUARTERPI = math.pi * .25

    minLat = -90
    maxLat = 90
    minLon = -180
    maxLon = 180

    def _shift_polygon(self, polygon):
        return [polygon]  # no shifting

    def plot(self, geometry):
        geometries = hasattr(geometry, 'geoms') and geometry.geoms or [geometry]
        res = []

        # at first shift polygons
        #shifted = []
        #for geom in geometries:
        #    if isinstance(geom, Polygon):
        #        shifted += self._shift_polygon(geom)
        #    else:
        #        shifted += [geom]

        for geom in geometries:
            if isinstance(geom, Polygon):
                res += self.plot_polygon(geom)
            elif isinstance(geom, LineString):
                rings = self.plot_linear_ring(geom)
                res += map(LineString, rings)
            elif isinstance(geom, Point):
                if self._visible(geom.x, geom.y):
                    x, y = self.project(geom.x, geom.y)
                    res.append(Point(x, y))
            else:
                pass
                # raise KartographError('proj.plot(): unknown geometry type %s' % geom)

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
                    return Point(res[0].x, res[0].y)

    def plot_polygon(self, polygon):
        ext = self.plot_linear_ring(polygon.exterior, truncate=True)
        if len(ext) == 1:
            pts_int = []
            for interior in polygon.interiors:
                pts_int += self.plot_linear_ring(interior, truncate=True)
            return [Polygon(ext[0], pts_int)]
        elif len(ext) == 0:
            return []
        else:
            raise KartographError('unhandled case: exterior is split into multiple rings')

    def plot_linear_ring(self, ring, truncate=False):
        ignore = True
        points = []
        for (lon, lat) in ring.coords:
            vis = self._visible(lon, lat)
            if vis:
                ignore = False
            x, y = self.project(lon, lat)
            if not vis and truncate:
                points.append(self._truncate(x, y))
            else:
                points.append((x, y))
        if ignore:
            return []
        return [points]

    def ll(self, lon, lat):
        return (lon, lat)

    def project(self, lon, lat):
        assert False, 'Proj is an abstract class'

    def project_inverse(self, x, y):
        assert False, 'inverse projection is not supporte by %s' % self.name

    def _visible(self, lon, lat):
        assert False, 'Proj is an abstract class'

    def _truncate(self, x, y):
        assert False, 'truncation is not implemented'

    def world_bounds(self, bbox, llbbox=(-180, -90, 180, 90)):
        sea = self.sea_shape(llbbox)
        for x, y in sea[0]:
            bbox.update((x, y))
        return bbox

    def bounding_geometry(self, llbbox=(-180, -90, 180, 90), projected=False):
        """
        returns a WGS84 polygon that represents the limits of this projection
        points that lie outside this polygon will not be plotted
        this polygon will also be used to render the sea layer in world maps

        defaults to full WGS84 range
        """
        from shapely.geometry import Polygon
        sea = []

        minLon = llbbox[0]
        maxLon = llbbox[2]
        minLat = max(self.minLat, llbbox[1])
        maxLat = min(self.maxLat, llbbox[3])

        def xfrange(start, stop, step):
            if stop > start:
                while start < stop:
                    yield start
                    start += step
            else:
                while stop < start:
                    yield start
                    start -= step

        lat_step = abs((maxLat - minLat) / 180.0)
        lon_step = abs((maxLon - minLon) / 360.0)

        for lat in xfrange(minLat, maxLat, lat_step):
            sea.append((minLon, lat))
        for lon in xfrange(minLon, maxLon, lon_step):
            sea.append((lon, maxLat))
        for lat in xfrange(maxLat, minLat, lat_step):
            sea.append((maxLon, lat))
        for lon in xfrange(maxLon, minLon, lon_step):
            sea.append((lon, minLat))

        if projected:
            sea = [self.project(lon, lat) for (lon, lat) in sea]

        return Polygon(sea)

    def __str__(self):
        return 'Proj(' + self.name + ')'

    def attrs(self):
        return dict(id=self.name)

    @staticmethod
    def attributes():
        """
        returns array of attribute names of this projection
        """
        return []

    @staticmethod
    def fromXML(xml, projections):
        id = xml['id']
        if id in projections:
            ProjClass = projections[id]
            args = {}
            for (prop, val) in xml:
                if prop[0] != "id":
                    args[prop[0]] = float(val)
            return ProjClass(**args)
        raise Exception("could not restore projection from xml")
