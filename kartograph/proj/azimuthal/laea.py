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
        self.proj = pyproj.Proj(proj='laea', lat_0=lat0, lon_0=lon0)
        Azimuthal.__init__(self, lat0, lon0)

    def project_proj4(self, lon, lat):
        return self.proj(lon, lat)

    def project_inverse(self, x, y):
        return self.proj(x, y, inverse=True)

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
