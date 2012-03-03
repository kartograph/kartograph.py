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

import math 
from math import radians as rad


class Proj(object):
    """
    base class for projections
    """    
    HALFPI = math.pi * .5
    QUARTERPI = math.pi * .25
    
    minLat = -90
    maxLat = 90
                    
    def plot(self, polygon, truncate=True):
        points = []
        ignore = True
        for (lon,lat) in polygon:
            vis = self._visible(lon, lat)
            if vis:
                ignore = False
            x,y = self.project(lon, lat)
            if not vis and truncate:
                points.append(self._truncate(x,y))
            else:
                points.append((x,y))
        if ignore:
            return None
        return [points]
        
    def ll(self, lon, lat):
        return (lon,lat)
    
    def project(self, lon, lat):
        assert False, 'Proj is an abstract class'
                
    def _visible(self, lon, lat):
        assert False, 'Proj is an abstract class'
    
    def _truncate(self, x, y):
        assert False, 'truncation is not implemented'
    
    def world_bounds(self, bbox, llbbox=(-180,-90,180,90)):
        sea = self.sea_shape(llbbox)
        for x,y in sea:
            bbox.update((x,y))
        return bbox        

    def sea_shape(self, llbbox=(-180,-90,180,90)):
        """
        returns non-projected multi-polygon map bounds
        """
        sea = []
        out = []
        
        minLon = llbbox[0]
        maxLon = llbbox[2]
        minLat = max(self.minLat, llbbox[1])
        maxLat = min(self.maxLat, llbbox[3])
        
        def xfrange(start, stop, step):
            if stop > start:
                while start < stop:
                    yield start
                    start += step
            else:
                while stop < start:
                    yield start
                    start -= step
    
        lat_step = abs((maxLat - minLat)/180.0)
        lon_step = abs((maxLon - minLon)/360.0)
        
        for lat in xfrange(minLat, maxLat, lat_step): sea.append((minLon,lat))
        for lon in xfrange(minLon, maxLon, lon_step): sea.append((lon, maxLat))
        for lat in xfrange(maxLat, minLat, lat_step): sea.append((maxLon, lat))
        for lon in xfrange(maxLon, minLon, lon_step): sea.append((lon, minLat))
        
        for s in sea:
            lon, lat = s
            out.append(self.project(lon, lat))
        
        return [out]    
        
    def __str__(self):
        return 'Proj('+self.name+')'
        
    def toXML(self):
        from svgfig import SVG
        p = SVG('proj', id=self.name)
        return p
    
    @staticmethod
    def attributes():
        """
        returns array of attribute names of this projection 
        """
        return []
    
    @staticmethod
    def fromXML(xml):
        id = xml['id']
        if id in projections:
            ProjClass = projections[id]
            args = {}
            for (prop,val) in xml:
                if prop[0] != "id":
                    args[prop[0]] = float(val)
            return ProjClass(**args)
        raise Exception("could not restore projection from xml")
        
