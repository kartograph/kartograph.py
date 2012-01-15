"""
as of version 2.0 kartograph supports multiple import formats

- Shapefile
- KML ? (only polygons and polylines)
- GeoJSON ?
"""

import errors

class LayerSource:
	
	def getGeometry(self, attr, value):
		raise NotImplementedError()
		
