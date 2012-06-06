"""
as of version 2.0 kartograph supports multiple import formats

- Shapefile
- KML ? (only polygons and polylines)
- GeoJSON ?
"""

__all__ = ['LayerSource', 'ShapefileLayer', 'GraticuleLayer']

from shplayer import ShapefileLayer
from layersource import LayerSource
from special import GraticuleLayer, SeaLayer
from kartograph.errors import *


def handle_layer_source(layer, cache={}):
    if 'src' in layer:
        src = layer['src']
        if src in cache:
            return cache[src]
        if src[-4:].lower() == ".shp":  # shapefile layer
            src = ShapefileLayer(src)
        if isinstance(src, LayerSource):
            cache[layer['src']] = src
            return src
        else:
            raise KartographLayerSourceError('don\'t know how to handle "' + src + '"')
    elif 'special' in layer:
        if layer['special'] == 'graticule':
            return GraticuleLayer()
        elif layer['special'] == 'sea':
            return SeaLayer()
