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
        
class Conic(Proj):
    def __init__(self, lat0=0, lon0=0, lat1=0, lat2=0):
        from math import radians as rad
        self.lat0 = lat0
        self.phi0 = rad(lat0)
        self.lon0 = lon0
        self.lam0 = rad(lon0)
        self.lat1 = lat1
        self.phi1 = rad(lat1)
        self.lat2 = lat2
        self.phi2 = rad(lat2)
        
    def _visible(self, lon, lat):
        return True
        
    def _truncate(self, x, y):
        return (x,y)
        
        
    def toXML(self):
        p = super(Conic, self).toXML()
        p['lon0'] = str(self.lon0)
        p['lat0'] = str(self.lat0)
        p['lat1'] = str(self.lat1)
        p['lat2'] = str(self.lat2)
        return p

    @staticmethod
    def attributes():
        return ['lon0','lat0','lat1','lat2']



class LCC(Conic):
    """
    Lambert Conformal Conic Projection (spherical)
    """
    def __init__(self, lat0=0, lon0=0, lat1=30, lat2=50):
        from math import sin,cos,tan,pow,log
        Conic.__init__(self, lat0=lat0, lon0=lon0, lat1=lat1, lat2=lat2)    
        self.n = n = sinphi = sin(self.phi1)
        cosphi = cos(self.phi1)
        secant = abs(self.phi1 - self.phi2) >= 1e-10
        
        if secant:
            n = log(cosphi / cos(self.phi2)) / log(tan(self.QUARTERPI + .5 * self.phi2) / tan(self.QUARTERPI + .5 * self.phi1))
        self.c = c = cosphi * pow(tan(self.QUARTERPI + .5 * self.phi1), n) / n
        if abs(abs(self.phi0) - self.HALFPI) < 1e-10:
            self.rho0 = 0.
        else:
            self.rho0 = c * pow(tan(self.QUARTERPI + .5 * self.phi0), -n)
            
        self.minLat = -60
        self.maxLat = 85
        
    def project(self, lon, lat):
        lon,lat = self.ll(lon, lat)
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
        
        return (x,y*-1)