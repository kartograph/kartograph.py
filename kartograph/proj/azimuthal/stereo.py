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


class Stereographic(Azimuthal):
    """
    Stereographic projection

    implementation taken from
    Snyder, Map projections - A working manual
    """
    def __init__(self, lat0=0.0, lon0=0.0):
        Azimuthal.__init__(self, lat0, lon0)

    def project(self, lon, lat):
        from math import radians as rad, cos, sin
        lon, lat = self.ll(lon, lat)
        phi = rad(lat)
        lam = rad(lon)

        k0 = 0.5
        k = 2 * k0 / (1 + sin(self.phi0) * sin(phi) + cos(self.phi0) * cos(phi) * cos(lam - self.lam0))

        xo = self.r * k * cos(phi) * sin(lam - self.lam0)
        yo = -self.r * k * (cos(self.phi0) * sin(phi) - sin(self.phi0) * cos(phi) * cos(lam - self.lam0))

        x = self.r + xo
        y = self.r + yo

        return (x, y)
