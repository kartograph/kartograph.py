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
import pyproj


class LAEA(Azimuthal):
    """
    Lambert Azimuthal Equal-Area Projection

    implementation taken from
    Snyder, Map projections - A working manual
    """
    def __init__(self, lon0=0.0, lat0=0.0):
        self.scale = math.sqrt(2) * 0.5
        Azimuthal.__init__(self, lat0, lon0)

    def project(self, lon, lat):
        # old projection code
        from math import radians as rad, pow, cos, sin
        # lon,lat = self.ll(lon, lat)
        phi = rad(lat)
        lam = rad(lon)

        if abs(lon - self.lon0) == 180:
            xo = self.r * 2
            yo = 0
        else:
            k = pow(2 / (1 + sin(self.phi0) * sin(phi) + cos(self.phi0) * cos(phi) * cos(lam - self.lam0)), .5)
            k *= self.scale  # .70738033

            xo = self.r * k * cos(phi) * sin(lam - self.lam0)
            yo = -self.r * k * (cos(self.phi0) * sin(phi) - sin(self.phi0) * cos(phi) * cos(lam - self.lam0))

        x = self.r + xo
        y = self.r + yo

        return (x, y)


class LAEA_Alaska(LAEA):
    def __init__(self, lon0=0, lat0=0):
        self.scale = math.sqrt(2) * 0.5 * 0.33
        Azimuthal.__init__(self, 90, -150)

class LAEA_Hawaii(LAEA):
    def __init__(self, lon0=0, lat0=0):
        self.scale = math.sqrt(2) * 0.5
        Azimuthal.__init__(self, 20, -157)


class LAEA_USA(LAEA):

    def __init__(self, lon0=0.0, lat0=0.0):
        self.scale = math.sqrt(2) * 0.5
        Azimuthal.__init__(self, 45, -100)
        self.LAEA_Alaska = LAEA_Alaska()
        self.LAEA_Hawaii = LAEA_Hawaii()

    def project(self, lon, lat):
        alaska = lat > 44 and (lon < -127 or lon > 170)
        hawaii = lon < -127 and lat < 44

        if alaska:
            if lon > 170:
                lon -= 380
            x,y = self.LAEA_Alaska.project(lon, lat)
        elif hawaii:
            x,y = self.LAEA_Hawaii.project(lon, lat)
        else:
            x,y = LAEA.project(self, lon, lat)

        if alaska:
            x += -180
            y += 100
        if hawaii:
            y += 220
            x += -80
        return (x,y)


class P4_LAEA(Azimuthal):
    """
    Lambert Azimuthal Equal-Area Projection

    implementation taken from
    Snyder, Map projections - A working manual
    """
    def __init__(self, lon0=0.0, lat0=0.0):
        self.scale = math.sqrt(2) * 0.5
        self.proj = pyproj.Proj(proj='laea', lat_0=lat0, lon_0=lon0)
        Azimuthal.__init__(self, lat0, lon0)

    def project(self, lon, lat):
        return self.proj(lon, lat)

    def project_inverse(self, x, y):
        return self.proj(x, y, inverse=True)

