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


class Azimuthal(Proj):

    def __init__(self, lat0=0.0, lon0=0.0, rad=1000):
        self.lat0 = lat0
        self.phi0 = math.radians(lat0)
        self.lon0 = lon0
        self.lam0 = math.radians(lon0)
        self.r = rad
        self.elevation0 = self.to_elevation(lat0)
        self.azimuth0 = self.to_azimuth(lon0)

    def to_elevation(self,latitude):
        return ((latitude + 90.0) / 180.0) * math.pi - math.pi/2

    def to_azimuth(self,longitude):
        return ((longitude + 180.0) / 360.0) * math.pi*2 - math.pi

    def _visible(self, lon, lat):
        elevation = self.to_elevation(lat)
        azimuth = self.to_azimuth(lon)
        # work out if the point is visible
        cosc = math.sin(elevation)*math.sin(self.elevation0)+math.cos(self.elevation0)*math.cos(elevation)*math.cos(azimuth-self.azimuth0)
        return cosc >= 0.0

    def _truncate(self, x, y):
        theta = math.atan2(y-self.r,x-self.r)
        x1 = self.r + self.r * math.cos(theta)
        y1 = self.r + self.r * math.sin(theta)
        return (x1,y1)

    def world_bounds(self, bbox, llbbox=(-180,-90,180,90)):
        if llbbox == (-180,-90,180,90):
            d = self.r*2
            bbox.update((0,0))
            bbox.update((d,d))
        else:
            bbox = super(Azimuthal, self).world_bounds(bbox, llbbox)
        return bbox

    def sea_shape(self, llbbox=(-180,-90,180,90)):
        out = []
        if llbbox == (-180,-90,180,90):
            for phi in range(0,360):
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
        xo = self.r * math.cos(elevation) * math.sin(azimuth-self.azimuth0)
        yo = -self.r * (math.cos(self.elevation0) * math.sin(elevation) - math.sin(self.elevation0) * math.cos(elevation) * math.cos(azimuth-self.azimuth0))
        x = self.r + xo
        y = self.r + yo
        return (x,y)



class LAEA(Azimuthal):
    """
    Lambert Azimuthal Equal-Area Projection

    implementation taken from
    Snyder, Map projections - A working manual
    """
    def __init__(self,lon0=0.0,lat0=0.0):
        import sys
        self.scale = math.sqrt(2)*0.5
        Azimuthal.__init__(self, lat0, lon0)

    def project(self, lon, lat):
        from math import radians as rad, pow, asin, cos, sin
        # lon,lat = self.ll(lon, lat)
        phi = rad(lat)
        lam = rad(lon)

        if False and abs(lon - self.lon0) == 180:
            xo = self.r*2
            yo = 0
        else:
            k = pow(2 / (1 + sin(self.phi0) * sin(phi) + cos(self.phi0)*cos(phi)*cos(lam - self.lam0)), .5)
            k *= self.scale#.70738033

            xo = self.r * k * cos(phi) * sin(lam - self.lam0)
            yo = -self.r * k * ( cos(self.phi0)*sin(phi) - sin(self.phi0)*cos(phi)*cos(lam - self.lam0) )

        x = self.r + xo
        y = self.r + yo

        return (x,y)



class Stereographic(Azimuthal):
    """
    Stereographic projection

    implementation taken from
    Snyder, Map projections - A working manual
    """
    def __init__(self,lat0=0.0,lon0=0.0):
        Azimuthal.__init__(self, lat0, lon0)

    def project(self, lon, lat):
        from math import radians as rad, pow, asin, cos, sin
        lon,lat = self.ll(lon, lat)
        phi = rad(lat)
        lam = rad(lon)

        k0 = 0.5
        k = 2*k0 / (1 + sin(self.phi0) * sin(phi) + cos(self.phi0)*cos(phi)*cos(lam - self.lam0))

        xo = self.r * k * cos(phi) * sin(lam - self.lam0)
        yo = -self.r * k * ( cos(self.phi0)*sin(phi) - sin(self.phi0)*cos(phi)*cos(lam - self.lam0) )

        x = self.r + xo
        y = self.r + yo

        return (x,y)



class Satellite(Azimuthal):
    """
    General perspective projection, aka Satellite projection

    implementation taken from
    Snyder, Map projections - A working manual

    up .. angle the camera is turned away from north (clockwise)
    tilt .. angle the camera is tilted
    """
    def __init__(self,lat0=0.0,lon0=0.0,dist=1.6,up=0, tilt=0):
        import sys
        Azimuthal.__init__(self, 0, 0)

        self.dist = dist
        self.up = up
        self.up_ = math.radians(up)
        self.tilt = tilt
        self.tilt_ = math.radians(tilt)

        self.scale = 1
        xmin = sys.maxint
        xmax = sys.maxint*-1
        for lat in range(0,180):
            for lon in range(0,361):
                x,y = self.project(lon-180,lat-90)
                xmin = min(x, xmin)
                xmax = max(x, xmax)
        self.scale = (self.r*2)/(xmax-xmin)

        Azimuthal.__init__(self, lat0, lon0)


    def project(self, lon, lat):
        from math import radians as rad, pow, asin, cos, sin
        lon,lat = self.ll(lon, lat)
        phi = rad(lat)
        lam = rad(lon)

        cos_c = sin(self.phi0) * sin(phi) + cos(self.phi0) * cos(phi) * cos(lam - self.lam0)
        k = (self.dist - 1) / (self.dist - cos_c)
        k = (self.dist - 1) / (self.dist - cos_c)

        k *= self.scale

        xo = self.r * k * cos(phi) * sin(lam - self.lam0)
        yo = -self.r * k * ( cos(self.phi0)*sin(phi) - sin(self.phi0)*cos(phi)*cos(lam - self.lam0) )

        # rotate
        tilt = self.tilt_

        cos_up = cos(self.up_)
        sin_up = sin(self.up_)
        cos_tilt = cos(tilt)
        sin_tilt = sin(tilt)

        H = self.r * (self.dist - 1)
        A = ((yo * cos_up + xo * sin_up) * sin(tilt/H)) + cos_tilt
        xt = (xo * cos_up - yo * sin_up) * cos(tilt/A)
        yt = (yo * cos_up + xo * sin_up) / A

        x = self.r + xt
        y = self.r + yt

        return (x,y)

    def _visible(self, lon, lat):
        elevation = self.to_elevation(lat)
        azimuth = self.to_azimuth(lon)
        # work out if the point is visible
        cosc = math.sin(elevation)*math.sin(self.elevation0)+math.cos(self.elevation0)*math.cos(elevation)*math.cos(azimuth-self.azimuth0)
        return cosc >= (1.0/self.dist)

    def attrs(self):
        p = super(Satellite, self).attrs()
        p['dist'] = self.dist
        p['up'] = self.up
        p['tilt'] = self.tilt
        return p

    def _truncate(self, x, y):
        theta = math.atan2(y-self.r,x-self.r)
        x1 = self.r + self.r * math.cos(theta)
        y1 = self.r + self.r * math.sin(theta)
        return (x1,y1)



class EquidistantAzimuthal(Azimuthal):
    """
    Equidistant Azimuthal projection

    implementation taken from
    Snyder, Map projections - A working manual
    """
    def __init__(self,lat0=0.0,lon0=0.0):
        Azimuthal.__init__(self, lat0, lon0)

    def project(self, lon, lat):
        from math import radians as rad, pow, asin, cos, sin

        phi = rad(lat)
        lam = rad(lon)

        cos_c = sin(self.phi0) * sin(phi) + cos(self.phi0) * cos(phi) * cos(lam - self.lam0)
        c = math.acos(cos_c)
        sin_c = sin(c)
        if sin_c == 0:
            k = 1
        else:
            k = 0.325 * c/sin(c)

        xo = self.r * k * cos(phi) * sin(lam - self.lam0)
        yo = -self.r * k * ( cos(self.phi0)*sin(phi) - sin(self.phi0)*cos(phi)*cos(lam - self.lam0) )

        x = self.r + xo
        y = self.r + yo

        return (x,y)

    def _visible(self, lon, lat):
        return True



class Aitoff(EquidistantAzimuthal):
    """
    Aitoff Azimuthal projection

    implementation taken from
    Snyder, Map projections - A working manual
    """
    def __init__(self,lat0=0.0,lon0=0.0):
        self.cosphi = 1
        EquidistantAzimuthal.__init__(self, lat0=0, lon0=lon0)

    def project(self, lon, lat):
        x,y = EquidistantAzimuthal.project(self, lon, lat)
        y *= .5
        return (x,y)

