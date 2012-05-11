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


class Orthographic(Azimuthal):
    """
    Orthographic Azimuthal Projection

    implementation taken from http://www.mccarroll.net/snippets/svgworld/
    """
    def __init__(self, lat0=0, lon0=0):
        self.r = 1000
        Azimuthal.__init__(self, lat0, lon0)

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        elevation = self.to_elevation(lat)
        azimuth = self.to_azimuth(lon)
        xo = self.r * math.cos(elevation) * math.sin(azimuth - self.azimuth0)
        yo = -self.r * (math.cos(self.elevation0) * math.sin(elevation) - math.sin(self.elevation0) * math.cos(elevation) * math.cos(azimuth - self.azimuth0))
        x = self.r + xo
        y = self.r + yo
        return (x, y)
