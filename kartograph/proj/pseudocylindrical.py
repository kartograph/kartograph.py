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

from cylindrical import Cylindrical
import math
from math import radians as rad


class PseudoCylindrical(Cylindrical):
    def __init__(self, lon0=0.0, flip=0):
        Cylindrical.__init__(self, lon0=lon0, flip=flip)


class NaturalEarth(PseudoCylindrical):
    """
    src: http://www.shadedrelief.com/NE_proj/
    """
    def __init__(self, lat0=0.0, lon0=0.0, flip=0):
        PseudoCylindrical.__init__(self, lon0=lon0, flip=flip)
        from math import pi
        s = self
        s.A0 = 0.8707
        s.A1 = -0.131979
        s.A2 = -0.013791
        s.A3 = 0.003971
        s.A4 = -0.001529
        s.B0 = 1.007226
        s.B1 = 0.015085
        s.B2 = -0.044475
        s.B3 = 0.028874
        s.B4 = -0.005916
        s.C0 = s.B0
        s.C1 = 3 * s.B1
        s.C2 = 7 * s.B2
        s.C3 = 9 * s.B3
        s.C4 = 11 * s.B4
        s.EPS = 1e-11
        s.MAX_Y = 0.8707 * 0.52 * pi

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        lplam = rad(lon)
        lpphi = rad(lat * -1)
        phi2 = lpphi * lpphi
        phi4 = phi2 * phi2
        x = lplam * (self.A0 + phi2 * (self.A1 + phi2 * (self.A2 + phi4 * phi2 * (self.A3 + phi2 * self.A4)))) * 180 + 500
        y = lpphi * (self.B0 + phi2 * (self.B1 + phi4 * (self.B2 + self.B3 * phi2 + self.B4 * phi4))) * 180 + 270
        return (x, y)


class Robinson(PseudoCylindrical):

    def __init__(self, lat0=0.0, lon0=0.0, flip=0):
        PseudoCylindrical.__init__(self, lon0=lon0, flip=flip)
        self.X = [1, -5.67239e-12, -7.15511e-05, 3.11028e-06,  0.9986, -0.000482241, -2.4897e-05, -1.33094e-06, 0.9954, -0.000831031, -4.4861e-05, -9.86588e-07, 0.99, -0.00135363, -5.96598e-05, 3.67749e-06, 0.9822, -0.00167442, -4.4975e-06, -5.72394e-06, 0.973, -0.00214869, -9.03565e-05, 1.88767e-08, 0.96, -0.00305084, -9.00732e-05, 1.64869e-06, 0.9427, -0.00382792, -6.53428e-05, -2.61493e-06, 0.9216, -0.00467747, -0.000104566, 4.8122e-06, 0.8962, -0.00536222, -3.23834e-05, -5.43445e-06, 0.8679, -0.00609364, -0.0001139, 3.32521e-06, 0.835, -0.00698325, -6.40219e-05, 9.34582e-07, 0.7986, -0.00755337, -5.00038e-05, 9.35532e-07, 0.7597, -0.00798325, -3.59716e-05, -2.27604e-06, 0.7186, -0.00851366, -7.0112e-05, -8.63072e-06, 0.6732, -0.00986209, -0.000199572, 1.91978e-05, 0.6213, -0.010418, 8.83948e-05, 6.24031e-06, 0.5722, -0.00906601, 0.000181999, 6.24033e-06, 0.5322,  0.,  0.,  0.]
        self.Y = [0, 0.0124, 3.72529e-10, 1.15484e-09, 0.062, 0.0124001, 1.76951e-08, -5.92321e-09, 0.124, 0.0123998, -7.09668e-08, 2.25753e-08, 0.186, 0.0124008, 2.66917e-07, -8.44523e-08, 0.248, 0.0123971, -9.99682e-07, 3.15569e-07, 0.31, 0.0124108, 3.73349e-06, -1.1779e-06, 0.372, 0.0123598, -1.3935e-05, 4.39588e-06, 0.434, 0.0125501, 5.20034e-05, -1.00051e-05, 0.4968, 0.0123198, -9.80735e-05, 9.22397e-06, 0.5571, 0.0120308, 4.02857e-05, -5.2901e-06, 0.6176, 0.0120369, -3.90662e-05, 7.36117e-07, 0.6769, 0.0117015, -2.80246e-05, -8.54283e-07, 0.7346, 0.0113572, -4.08389e-05, -5.18524e-07, 0.7903, 0.0109099, -4.86169e-05, -1.0718e-06, 0.8435, 0.0103433, -6.46934e-05, 5.36384e-09, 0.8936, 0.00969679, -6.46129e-05, -8.54894e-06, 0.9394, 0.00840949, -0.000192847, -4.21023e-06, 0.9761, 0.00616525, -0.000256001, -4.21021e-06, 1.,  0.,  0.,  0]
        self.NODES = 18
        self.FXC = 0.8487
        self.FYC = 1.3523
        self.C1 = 11.45915590261646417544
        self.RC1 = 0.08726646259971647884
        self.ONEEPS = 1.000001
        self.EPS = 1e-8

    def _poly(self, arr, off, z):
        return arr[off] + z * (arr[off + 1] + z * (arr[off + 2] + z * (arr[off + 3])))

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        lplam = rad(lon)
        lpphi = rad(lat * -1)

        phi = abs(lpphi)
        i = int(phi * self.C1)
        if i >= self.NODES:
            i = self.NODES - 1
        phi = math.degrees(phi - self.RC1 * i)
        i *= 4
        x = 1000 * self._poly(self.X, i, phi) * self.FXC * lplam
        y = 1000 * self._poly(self.Y, i, phi) * self.FYC
        if lpphi < 0.0:
            y = -y

        return (x, y)


class EckertIV(PseudoCylindrical):

    def __init__(self, lon0=0.0, lat0=0, flip=0):
        PseudoCylindrical.__init__(self, lon0=lon0, flip=flip)

        self.C_x = .42223820031577120149
        self.C_y = 1.32650042817700232218
        self.RC_y = .75386330736002178205
        self.C_p = 3.57079632679489661922
        self.RC_p = .28004957675577868795
        self.EPS = 1e-7
        self.NITER = 6

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        lplam = rad(lon)
        lpphi = rad(lat * -1)

        p = self.C_p * math.sin(lpphi)
        V = lpphi * lpphi
        lpphi *= 0.895168 + V * (0.0218849 + V * 0.00826809)

        i = self.NITER
        while i > 0:
            c = math.cos(lpphi)
            s = math.sin(lpphi)
            V = (lpphi + s * (c + 2.) - p) / (1. + c * (c + 2.) - s * s)
            lpphi -= V
            if abs(V) < self.EPS:
                break
            i -= 1

        if i == 0:
            x = self.C_x * lplam
            y = (self.C_y, - self.C_y)[lpphi < 0]
        else:
            x = self.C_x * lplam * (1. + math.cos(lpphi))
            y = self.C_y * math.sin(lpphi)
        return (x, y)


class Sinusoidal(PseudoCylindrical):

    def __init__(self, lon0=0.0, lat0=0.0, flip=0):
        PseudoCylindrical.__init__(self, lon0=lon0, flip=flip)

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        lam = rad(lon)
        phi = rad(lat * -1)
        x = 1032 * lam * math.cos(phi)
        y = 1032 * phi
        return (x, y)


class Mollweide(PseudoCylindrical):

    def __init__(self, p=1.5707963267948966, lon0=0.0, lat0=0.0, cx=None, cy=None, cp=None, flip=0):
        PseudoCylindrical.__init__(self, lon0=lon0, flip=flip)
        self.MAX_ITER = 10
        self.TOLERANCE = 1e-7

        if p != None:
            p2 = p + p
            sp = math.sin(p)
            r = math.sqrt(math.pi * 2.0 * sp / (p2 + math.sin(p2)))
            self.cx = 2. * r / math.pi
            self.cy = r / sp
            self.cp = p2 + math.sin(p2)
        elif cx != None and cy != None and cp != None:
            self.cx = cx
            self.cy = cy
            self.cp = cp
        else:
            assert False, 'either p or cx,cy,cp must be defined'

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        lam = rad(lon)
        phi = rad(lat)

        k = self.cp * math.sin(phi)
        i = self.MAX_ITER

        while i != 0:
            v = (phi + math.sin(phi) - k) / (1. + math.cos(phi))
            phi -= v
            if abs(v) < self.TOLERANCE:
                break
            i -= 1

        if i == 0:
            phi = (self.HALFPI, -self.HALFPI)[phi < 0]
        else:
            phi *= 0.5

        x = 1000 * self.cx * lam * math.cos(phi)
        y = 1000 * self.cy * math.sin(phi)
        return (x, y * -1)


class GoodeHomolosine(PseudoCylindrical):

    def __init__(self, lon0=0, flip=0):
        self.lat1 = 41.737
        PseudoCylindrical.__init__(self, lon0=lon0, flip=flip)
        self.p1 = Mollweide()
        self.p0 = Sinusoidal()

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        #lon = me.clon(lon)
        if abs(lat) > self.lat1:
            return self.p1.project(lon, lat)
        else:
            return self.p0.project(lon, lat)


class WagnerIV(Mollweide):
    def __init__(self, lon0=0, lat0=0, flip=0):
        # p=math.pi/3
        Mollweide.__init__(self, p=1.0471975511965976, flip=flip)


class WagnerV(Mollweide):
    def __init__(self, lat0=0, lon0=0, flip=0):
        Mollweide.__init__(self, cx=0.90977, cy=1.65014, cp=3.00896, flip=flip)


class Loximuthal(PseudoCylindrical):

    minLat = -89
    maxLat = 89

    def __init__(self, lon0=0.0, lat0=0.0, flip=0):
        PseudoCylindrical.__init__(self, lon0=lon0, flip=flip)
        if flip == 1:
            lat0 = -lat0
        self.lat0 = lat0
        self.phi0 = rad(lat0)

    def project(self, lon, lat):
        lon, lat = self.ll(lon, lat)
        lam = rad(lon)
        phi = rad(lat)
        if phi == self.phi0:
            x = lam * math.cos(self.phi0)
        else:
            try:
                x = lam * (phi - self.phi0) / (math.log(math.tan(self.QUARTERPI + phi * 0.5)) - math.log(math.tan(self.QUARTERPI + self.phi0 * 0.5)))
            except:
                return None
        x *= 1000
        y = 1000 * (phi - self.phi0)
        return (x, y * -1)

    def attrs(self):
        p = super(Loximuthal, self).attrs()
        p['lat0'] = self.lat0
        return p

    @staticmethod
    def attributes():
        return ['lon0', 'lat0', 'flip']


class CantersModifiedSinusoidalI(PseudoCylindrical):
    """
    Canters, F. (2002) Small-scale Map projection Design. p. 218-219.
    Modified Sinusoidal, equal-area.

    implementation borrowed from
    http://cartography.oregonstate.edu/temp/AdaptiveProjection/src/projections/Canters1.js
    """

    def __init__(self, lon0=0.0, flip=0):
        PseudoCylindrical.__init__(self, lon0=lon0, flip=flip)
        self.C1 = 1.1966
        self.C3 = -0.1290
        self.C3x3 = 3 * self.C3
        self.C5 = -0.0076
        self.C5x5 = 5 * self.C5

    def project(self, lon, lat):
        me = self
        lon, lat = me.ll(lon, lat)

        lon = rad(lon)
        lat = rad(lat)

        y2 = lat * lat
        y4 = y2 * y2
        x = 1000 * lon * math.cos(lat) / (me.C1 + me.C3x3 * y2 + me.C5x5 * y4)
        y = 1000 * lat * (me.C1 + me.C3 * y2 + me.C5 * y4)
        return (x, y * -1)


class Hatano(PseudoCylindrical):

    def __init__(me, lon0=0, flip=0):
        PseudoCylindrical.__init__(me, lon0=lon0, flip=flip)
        me.NITER = 20
        me.EPS = 1e-7
        me.ONETOL = 1.000001
        me.CN = 2.67595
        me.CS = 2.43763
        me.RCN = 0.37369906014686373063
        me.RCS = 0.41023453108141924738
        me.FYCN = 1.75859
        me.FYCS = 1.93052
        me.RYCN = 0.56863737426006061674
        me.RYCS = 0.51799515156538134803
        me.FXC = 0.85
        me.RXC = 1.17647058823529411764

    def project(me, lon, lat):
        [lon, lat] = me.ll(lon, lat)
        lam = rad(lon)
        phi = rad(lat)
        c = math.sin(phi) * (me.CN, me.CS)[phi < 0.0]
        for i in range(me.NITER, 0, -1):
            th1 = (phi + math.sin(phi) - c) / (1.0 + math.cos(phi))
            phi -= th1
            if abs(th1) < me.EPS:
                break
        phi *= 0.5
        x = 1000 * me.FXC * lam * math.cos(phi)
        y = 1000 * math.sin(phi) * (me.FYCN, me.FYCS)[phi < 0.0]
        return (x, y * -1)


class Aitoff(PseudoCylindrical):
    """
    Aitoff projection

    implementation taken from
    Snyder, Map projections - A working manual
    """
    def __init__(self, lon0=0, flip=0):
        PseudoCylindrical.__init__(self, lon0=lon0, flip=flip)
        self.winkel = False
        self.COSPHI1 = 0.636619772367581343

    def project(me, lon, lat):
        [lon, lat] = me.ll(lon, lat)
        lam = rad(lon)
        phi = rad(lat)
        c = 0.5 * lam
        d = math.acos(math.cos(phi) * math.cos(c))
        if d != 0:
            y = 1.0 / math.sin(d)
            x = 2.0 * d * math.cos(phi) * math.sin(c) * y
            y *= d * math.sin(phi)
        else:
            x = y = 0
        if me.winkel:
            x = (x + lam * me.COSPHI1) * 0.5
            y = (y + phi) * 0.5
        return (x * 1000, y * -1000)


class Winkel3(Aitoff):

    def __init__(self, lon0=0, flip=0):
        Aitoff.__init__(self, lon0=lon0, flip=flip)
        self.winkel = True


class Nicolosi(PseudoCylindrical):

    def __init__(me, lon0=0, flip=0):
        me.EPS = 1e-10
        PseudoCylindrical.__init__(me, lon0=lon0, flip=flip)
        me.r = me.HALFPI * 100
        sea = []
        r = me.r
        for phi in range(0, 361):
            sea.append((math.cos(rad(phi)) * r, math.sin(rad(phi)) * r))
        me.sea = sea

    def _clon(me, lon):
        lon -= me.lon0
        if lon < -180:
            lon += 360
        elif lon > 180:
            lon -= 360
        return lon

    def _visible(me, lon, lat):
        #lon = me._clon(lon)
        return lon > -90 and lon < 90

    def _truncate(me, x, y):
        theta = math.atan2(y, x)
        x1 = me.r * math.cos(theta)
        y1 = me.r * math.sin(theta)
        return (x1, y1)

    def world_bounds(self, bbox, llbbox=(-180, -90, 180, 90)):
        if llbbox == (-180, -90, 180, 90):
            d = self.r * 2
            bbox.update((-d, -d))
            bbox.update((d, d))
        else:
            bbox = super(PseudoCylindrical, self).world_bounds(bbox, llbbox)
        return bbox

    def sea_shape(self, llbbox=(-180, -90, 180, 90)):
        out = []
        if llbbox == (-180, -90, 180, 90) or llbbox == [-180, -90, 180, 90]:
            for phi in range(0, 360):
                x = math.cos(math.radians(phi)) * self.r
                y = math.sin(math.radians(phi)) * self.r
                out.append((x, y))
            out = [out]
        else:
            out = super(PseudoCylindrical, self).sea_shape(llbbox)
        return out

    def project(me, lon, lat):
        [lon, lat] = me.ll(lon, lat)
        lam = rad(lon)
        phi = rad(lat)

        if abs(lam) < me.EPS:
            x = 0
            y = phi
        elif abs(phi) < me.EPS:
            x = lam
            y = 0
        elif abs(abs(lam) - me.HALFPI) < me.EPS:
            x = lam * math.cos(phi)
            y = me.HALFPI * math.sin(phi)
        elif abs(abs(phi) - me.HALFPI) < me.EPS:
            x = 0
            y = phi
        else:
            tb = me.HALFPI / lam - lam / me.HALFPI
            c = phi / me.HALFPI
            sp = math.sin(phi)
            d = (1 - c * c) / (sp - c)
            r2 = tb / d
            r2 *= r2
            m = (tb * sp / d - 0.5 * tb) / (1.0 + r2)
            n = (sp / r2 + 0.5 * d) / (1.0 + 1.0 / r2)
            x = math.cos(phi)
            x = math.sqrt(m * m + x * x / (1.0 + r2))
            x = me.HALFPI * (m + (x, -x)[lam < 0])
            f = n * n - (sp * sp / r2 + d * sp - 1.0) / (1.0 + 1.0 / r2)
            if f < 0:
                y = phi
            else:
                y = math.sqrt(f)
                y = me.HALFPI * (n + (-y, y)[phi < 0])
        return (x * 100, y * -100)

    def plot(self, polygon, truncate=True):
        polygons = self._shift_polygon(polygon)
        plotted = []
        for polygon in polygons:
            points = []
            ignore = True
            for (lon, lat) in polygon:
                vis = self._visible(lon, lat)
                if vis:
                    ignore = False
                x, y = self.project(lon, lat)
                if not vis and truncate:
                    points.append(self._truncate(x, y))
                else:
                    points.append((x, y))
            if ignore:
                continue
            plotted.append(points)
        return plotted
