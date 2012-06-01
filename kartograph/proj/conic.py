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


class Conic(Proj):

    def __init__(self, lat0=0, lon0=0, lat1=0, lat2=0):
        self.lat0 = lat0
        self.phi0 = rad(lat0)
        self.lon0 = lon0
        self.lam0 = rad(lon0)
        self.lat1 = lat1
        self.phi1 = rad(lat1)
        self.lat2 = lat2
        self.phi2 = rad(lat2)

        if lon0 != 0.0:
            self.bounds = self.bounding_geometry()

    def _visible(self, lon, lat):
        return True

    def _truncate(self, x, y):
        return (x, y)

    def attrs(self):
        p = super(Conic, self).attrs()
        p['lon0'] = self.lon0
        p['lat0'] = self.lat0
        p['lat1'] = self.lat1
        p['lat2'] = self.lat2
        return p

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

    @staticmethod
    def attributes():
        return ['lon0', 'lat0', 'lat1', 'lat2']


class LCC(Conic):
    """
    Lambert Conformal Conic Projection (spherical)
    """
    def __init__(self, lat0=0, lon0=0, lat1=30, lat2=50):
        from math import sin, cos, tan, pow, log
        self.minLat = -60
        self.maxLat = 85
        Conic.__init__(self, lat0=lat0, lon0=lon0, lat1=lat1, lat2=lat2)
        self.n = n = sin(self.phi1)
        cosphi = cos(self.phi1)
        secant = abs(self.phi1 - self.phi2) >= 1e-10
        if secant:
            n = log(cosphi / cos(self.phi2)) / log(tan(self.QUARTERPI + .5 * self.phi2) / tan(self.QUARTERPI + .5 * self.phi1))
        self.c = c = cosphi * pow(tan(self.QUARTERPI + .5 * self.phi1), n) / n
        if abs(abs(self.phi0) - self.HALFPI) < 1e-10:
            self.rho0 = 0.
        else:
            self.rho0 = c * pow(tan(self.QUARTERPI + .5 * self.phi0), -n)


    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        phi = rad(lat)
        lam = rad(lon)
        n = self.n
        if abs(abs(phi) - self.HALFPI) < 1e-10:
            rho = 0.0
        else:
            rho = self.c * math.pow(math.tan(self.QUARTERPI + 0.5 * phi), -n)
        lam_ = (lam - self.lam0) * n
        x = 1000 * rho * math.sin(lam_)
        y = 1000 * (self.rho0 - rho * math.cos(lam_))

        return (x, y * -1)
