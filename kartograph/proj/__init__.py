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

projections = dict()

from base import Proj
from cylindrical import *

projections['lonlat'] = Equirectangular
projections['cea'] = CEA
projections['gallpeters'] = GallPeters
projections['hobodyer'] = HoboDyer
projections['behrmann'] = Behrmann
projections['balthasart'] = Balthasart
projections['mercator'] = Mercator
projections['ll'] = LonLat

from pseudocylindrical import *

projections['naturalearth'] = NaturalEarth
projections['robinson'] = Robinson
projections['eckert4'] = EckertIV
projections['sinusoidal'] = Sinusoidal
projections['mollweide'] = Mollweide
projections['wagner4'] = WagnerIV
projections['wagner5'] = WagnerV
projections['loximuthal'] = Loximuthal

from azimuthal import *

projections['ortho'] = Orthographic
projections['laea'] = LAEA
projections['stereo'] = Stereographic
projections['satellite'] = Satellite
projections['eda'] = EquidistantAzimuthal
projections['aitoff'] = Aitoff

from conic import *
        
projections['lcc'] = LCC


class Proj4(Proj):
    
    def __init__(self, projstr):
        import pyproj
        self.proj = pyproj.Proj(projstr)
        
    def project(self, lon, lat):
        lon,lat = self.ll(lon, lat)
        x,y = self.proj(lon, lat)
        return (x,y*-1)


class LCC__(Proj4):
    
    def __init__(self, lat0=0, lon0=0, lat1=28, lat2=30):
        Proj4.__init__(self, '+proj=lcc +lat_0=%f +lon_0=%f +lat_1=%f +lat_2=%f' % (lat0, lon0, lat1, lat2))
        
    def _visible(self, lon, lat):
        return True
        
    def _truncate(self, x,y):
        return (x,y)



for pjname in projections:
    projections[pjname].name = pjname
        
        
if __name__ == '__main__':
    import sys
    # some class testing
    #p = LAEA(52.0,10.0)
    #x,y = p.project(50,5)
    #assert (round(x,2),round(y,2)) == (3962799.45, -2999718.85), 'LAEA proj error'
    
    print Proj.fromXML(Robinson(lat0=3, lon0=4).toXML())
    
    Robinson(lat0=3, lon0=4)
    
    for pj in projections:
        Proj = projections[pj]
        try:
            proj = Proj(lat0=34.0, lon0=60)
            proj.project(0,0)
            proj.world_bounds()
            print proj.toXML()
        except:
            print 'Error', pj
            print sys.exc_info()[0]
            raise