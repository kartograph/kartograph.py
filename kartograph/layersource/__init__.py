"""
as of version 2.0 kartograph supports multiple import formats

- Shapefile
- KML ? (only polygons and polylines)
- GeoJSON ?
"""

__all__ = ['LayerSource', 'ShapefileLayer']

from shplayer import ShapefileLayer
from layersource import LayerSource
from kartograph.errors import *


def handle_layer_source(src):
	if src[-4:].lower() == ".shp": # shapefile layer
		src = ShapefileLayer(src)
	if isinstance(src, LayerSource):
		 return src
	else:
		raise KartographLayerSourceError('don\'t know how to handle "'+src+'"')