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

from base import Proj
import math
from math import radians as rad


class Cylindrical(Proj):

    def __init__(self, lon0=0.0, flip=0):
        self.flip = flip
        self.lon0 = lon0
        self.bounds = self.bounding_geometry()

    def _shift_polygon(self, polygon):
        """
        shifts a polygon according to the origin longitude
        """
        if self.lon0 == 0.0:
            return [polygon]  # no need to shift anything

        from shapely.geometry import Polygon
        # we need to split and join some polygons
        poly_coords = []
        holes = []
        for (lon, lat) in polygon.exterior.coords:
            poly_coords.append((lon - self.lon0, lat))
        for hole in polygon.interiors:
            hole_coords = []
            for (lon, lat) in hole.coords:
                hole_coords.append((lon - self.lon0, lat))
            holes.append(hole_coords)
        poly = Polygon(poly_coords, holes)

        polygons = []

        #print "shifted polygons", (time.time() - start)
        #start = time.time()

        try:
            p_in = poly.intersection(self.bounds)
            polygons += hasattr(p_in, 'geoms') and p_in.geoms or [p_in]
        except:
            pass

        #print "computed polygons inside bounds", (time.time() - start)
        #start = time.time()

        try:
            p_out = poly.symmetric_difference(self.bounds)
            out_geoms = hasattr(p_out, 'geoms') and p_out.geoms or [p_out]
        except:
            out_geoms = []
            pass

        #print "computed polygons outside bounds", (time.time() - start)
        #start = time.time()

        for polygon in out_geoms:
            ext_pts = []
            int_pts = []
            s = 0  # at first we compute the avg longitude
            c = 0
            for (lon, lat) in polygon.exterior.coords:
                s += lon
                c += 1
            left = s / float(c) < -180  # and use it to decide where to shift the polygon
            for (lon, lat) in polygon.exterior.coords:
                ext_pts.append((lon + (-360, 360)[left], lat))
            for interior in polygon.interiors:
                pts = []
                for (lon, lat) in interior.coords:
                    pts.append((lon + (-360, 360)[left], lat))
                int_pts.append(pts)
            polygons.append(Polygon(ext_pts, int_pts))

        # print "shifted outside polygons to inside", (time.time() - start)

        return polygons

    def _visible(self, lon, lat):
        return True

    def _truncate(self, x, y):
        return (x, y)

    def attrs(self):
        a = super(Cylindrical, self).attrs()
        a['lon0'] = self.lon0
        a['flip'] = self.flip
        return a

    def __str__(self):
        return 'Proj(' + self.name + ', lon0=%s)' % self.lon0

    @staticmethod
    def attributes():
        return ['lon0', 'flip']

    def ll(self, lon, lat):
        if self.flip == 1:
            return (-lon, -lat)
        return (lon, lat)


class Equirectangular(Cylindrical):
    """
    Equirectangular Projection, aka lonlat, aka plate carree
    """
    def __init__(self, lon0=0.0, lat0=0.0, flip=0):
        self.lat0 = lat0
        self.phi0 = rad(lat0 * -1)
        Cylindrical.__init__(self, lon0=lon0, flip=flip)

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        return (lon * math.cos(self.phi0) * 1000, lat * -1 * 1000)


class CEA(Cylindrical):
    """
    Cylindrical Equal Area Projection
    """
    def __init__(self, lat0=0.0, lon0=0.0, lat1=0.0, flip=0):
        self.lat0 = lat0
        self.lat1 = lat1
        self.phi0 = rad(lat0 * -1)
        self.phi1 = rad(lat1 * -1)
        self.lam0 = rad(lon0)
        Cylindrical.__init__(self, lon0=lon0, flip=flip)

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        lam = rad(lon)
        phi = rad(lat * -1)
        x = (lam) * math.cos(self.phi1) * 1000
        y = math.sin(phi) / math.cos(self.phi1) * 1000
        return (x, y)

    def attrs(self):
        p = super(CEA, self).attrs()
        p['lat1'] = self.lat1
        return p

    @staticmethod
    def attributes():
        return ['lon0', 'lat1', 'flip']

    def __str__(self):
        return 'Proj(' + self.name + ', lon0=%s, lat1=%s)' % (self.lon0, self.lat1)


class GallPeters(CEA):
    def __init__(self, lat0=0.0, lon0=0.0, flip=0):
        CEA.__init__(self, lon0=lon0, lat0=0, lat1=45, flip=flip)


class HoboDyer(CEA):
    def __init__(self, lat0=0.0, lon0=0.0, flip=0):
        CEA.__init__(self, lon0=lon0, lat0=lat0, lat1=37.5, flip=flip)


class Behrmann(CEA):
    def __init__(self, lat0=0.0, lon0=0.0, flip=0):
        CEA.__init__(self, lat1=30, lat0=lat0, lon0=lon0, flip=flip)


class Balthasart(CEA):
    def __init__(self, lat0=0.0, lon0=0.0, flip=0):
        CEA.__init__(self, lat1=50, lat0=lat0, lon0=lon0, flip=flip)


class Mercator(Cylindrical):
    def __init__(self, lon0=0.0, lat0=0.0, flip=0):
        Cylindrical.__init__(self, lon0=lon0, flip=flip)
        self.minLat = -85
        self.maxLat = 85

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        lam = rad(lon)
        phi = rad(lat * -1)
        x = lam * 1000
        y = math.log((1 + math.sin(phi)) / math.cos(phi)) * 1000
        return (x, y)


class LonLat(Cylindrical):
    def project(self, lon, lat):
        return (lon, lat)
