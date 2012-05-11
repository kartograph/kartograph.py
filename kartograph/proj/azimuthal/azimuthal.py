"""
    kartograph - a svg mapping library
    Copyright (C) 2011,2012  Gregor Aisch

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
from kartograph.proj.base import Proj


class Azimuthal(Proj):

    def __init__(self, lat0=0.0, lon0=0.0, rad=1000):
        self.lat0 = lat0
        self.phi0 = math.radians(lat0)
        self.lon0 = lon0
        self.lam0 = math.radians(lon0)
        self.r = rad
        self.elevation0 = self.to_elevation(lat0)
        self.azimuth0 = self.to_azimuth(lon0)

    def to_elevation(self, latitude):
        return ((latitude + 90.0) / 180.0) * math.pi - math.pi / 2.0

    def to_azimuth(self, longitude):
        return ((longitude + 180.0) / 360.0) * math.pi * 2 - math.pi

    def _visible(self, lon, lat):
        elevation = self.to_elevation(lat)
        azimuth = self.to_azimuth(lon)
        # work out if the point is visible
        cosc = math.sin(elevation) * math.sin(self.elevation0) + math.cos(self.elevation0) * math.cos(elevation) * math.cos(azimuth - self.azimuth0)
        return cosc >= 0.0

    def _truncate(self, x, y):
        theta = math.atan2(y - self.r, x - self.r)
        x1 = self.r + self.r * math.cos(theta)
        y1 = self.r + self.r * math.sin(theta)
        return (x1, y1)

    def world_bounds(self, bbox, llbbox=(-180, -90, 180, 90)):
        if llbbox == (-180, -90, 180, 90):
            d = self.r * 4
            bbox.update((0, 0))
            bbox.update((d, d))
        else:
            bbox = super(Azimuthal, self).world_bounds(bbox, llbbox)
        return bbox

    def sea_shape(self, llbbox=(-180, -90, 180, 90)):
        out = []
        if llbbox == (-180, -90, 180, 90) or llbbox == [-180, -90, 180, 90]:
            print "-> full extend"
            for phi in range(0, 360):
                x = self.r + math.cos(math.radians(phi)) * self.r
                y = self.r + math.sin(math.radians(phi)) * self.r
                out.append((x, y))
            out = [out]
        else:
            out = super(Azimuthal, self).sea_shape(llbbox)
        return out

    def attrs(self):
        p = super(Azimuthal, self).attrs()
        p['lon0'] = self.lon0
        p['lat0'] = self.lat0
        return p

    def __str__(self):
        return 'Proj(' + self.name + ', lon0=%s, lat0=%s)' % (self.lon0, self.lat0)

    @staticmethod
    def attributes():
        return ['lon0', 'lat0']
