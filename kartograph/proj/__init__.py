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
projections['canters1'] = CantersModifiedSinusoidalI
projections['goodehomolosine'] = GoodeHomolosine
projections['hatano'] = Hatano
projections['aitoff'] = Aitoff
projections['winkel3'] = Winkel3
projections['nicolosi'] = Nicolosi

from azimuthal import *

projections['ortho'] = Orthographic
projections['laea'] = LAEA
projections['laea-usa'] = LAEA_USA
projections['p4.laea'] = P4_LAEA
projections['stereo'] = Stereographic
projections['satellite'] = Satellite
projections['eda'] = EquidistantAzimuthal
projections['aitoff'] = Aitoff

from conic import *

projections['lcc'] = LCC

from proj4 import Proj4

projections['proj4'] = Proj4

for pjname in projections:
    projections[pjname].name = pjname


if __name__ == '__main__':
    import sys
    # some class testing
    #p = LAEA(52.0,10.0)
    #x,y = p.project(50,5)
    #assert (round(x,2),round(y,2)) == (3962799.45, -2999718.85), 'LAEA proj error'
    from kartograph.geometry import BBox

    print Proj.fromXML(Robinson(lat0=3, lon0=4).toXML(), projections)

    Robinson(lat0=3, lon0=4)

    for pj in projections:
        Proj = projections[pj]
        bbox = BBox()
        try:
            proj = Proj(lon0=60)
            print proj.project(0, 0)
            print proj.world_bounds(bbox)
            print proj.toXML()
        except:
            print 'Error', pj
            print sys.exc_info()[0]
            raise
