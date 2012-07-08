"""
as of version 2.0 kartograph supports multiple import formats

- Shapefile
- KML ? (only polygons and polylines)
- GeoJSON ?
"""

__all__ = ['LayerSource', 'ShapefileLayer', 'GraticuleLayer', 'OpenStreetMapLayer']

from shplayer import ShapefileLayer
from osmlayer import OpenStreetMapLayer
from layersource import LayerSource
from special import GraticuleLayer, SeaLayer
from kartograph.errors import *


def handle_layer_source(layer, cache={}):
    """
    ## handle_layer_source

    Tries to find out the type of the layer source.
    """
    if 'src' in layer:
        src = layer['src']
        # If the source is already stored in cache, we re-use it-
        if src in cache:
            return cache[src]
        # If the source url ends with ".shp", we will use the Shapefile reader
        if src[-4:].lower() == ".shp":
            src = ShapefileLayer(src)
        if src[:4] == "osm:":
            src = OpenStreetMapLayer(src[4:], osm_query=layer['osm-query'], osm_type=layer['osm-type'])
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
            