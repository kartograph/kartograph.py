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

from azimuthal import Azimuthal
import math


class Satellite(Azimuthal):
    """
    General perspective projection, aka Satellite projection

    implementation taken from
    Snyder, Map projections - A working manual

    up .. angle the camera is turned away from north (clockwise)
    tilt .. angle the camera is tilted
    """
    def __init__(self, lat0=0.0, lon0=0.0, dist=1.6, up=0, tilt=0):
        import sys
        Azimuthal.__init__(self, 0, 0)

        self.dist = dist
        self.up = up
        self.up_ = math.radians(up)
        self.tilt = tilt
        self.tilt_ = math.radians(tilt)

        self.scale = 1
        xmin = sys.maxint
        xmax = sys.maxint * -1
        for lat in range(0, 180):
            for lon in range(0, 361):
                x, y = self.project(lon - 180, lat - 90)
                xmin = min(x, xmin)
                xmax = max(x, xmax)
        self.scale = (self.r * 2) / (xmax - xmin)

        Azimuthal.__init__(self, lat0, lon0)

    def project(self, lon, lat):
        from math import radians as rad, cos, sin
        lon, lat = self.ll(lon, lat)
        phi = rad(lat)
        lam = rad(lon)

        cos_c = sin(self.phi0) * sin(phi) + cos(self.phi0) * cos(phi) * cos(lam - self.lam0)
        k = (self.dist - 1) / (self.dist - cos_c)
        k = (self.dist - 1) / (self.dist - cos_c)

        k *= self.scale

        xo = self.r * k * cos(phi) * sin(lam - self.lam0)
        yo = -self.r * k * (cos(self.phi0) * sin(phi) - sin(self.phi0) * cos(phi) * cos(lam - self.lam0))

        # rotate
        tilt = self.tilt_

        cos_up = cos(self.up_)
        sin_up = sin(self.up_)
        cos_tilt = cos(tilt)
        # sin_tilt = sin(tilt)

        H = self.r * (self.dist - 1)
        A = ((yo * cos_up + xo * sin_up) * sin(tilt / H)) + cos_tilt
        xt = (xo * cos_up - yo * sin_up) * cos(tilt / A)
        yt = (yo * cos_up + xo * sin_up) / A

        x = self.r + xt
        y = self.r + yt

        return (x, y)

    def _visible(self, lon, lat):
        elevation = self.to_elevation(lat)
        azimuth = self.to_azimuth(lon)
        # work out if the point is visible
        cosc = math.sin(elevation) * math.sin(self.elevation0) + math.cos(self.elevation0) * math.cos(elevation) * math.cos(azimuth - self.azimuth0)
        return cosc >= (1.0 / self.dist)

    def attrs(self):
        p = super(Satellite, self).attrs()
        p['dist'] = self.dist
        p['up'] = self.up
        p['tilt'] = self.tilt
        return p

    def _truncate(self, x, y):
        theta = math.atan2(y - self.r, x - self.r)
        x1 = self.r + self.r * math.cos(theta)
        y1 = self.r + self.r * math.sin(theta)
        return (x1, y1)
