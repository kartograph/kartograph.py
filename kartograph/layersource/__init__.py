"""
as of version 2.0 kartograph supports multiple import formats

- Shapefile
- KML ? (only polygons and polylines)
- GeoJSON ?
"""

__all__ = ['LayerSource', 'ShapefileLayer', 'CsvLayer', 'GraticuleLayer', 'PostGISLayer']

from shplayer import ShapefileLayer
from csvlayer import CsvLayer
from postgislayer import PostGISLayer
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
            if isinstance(src, LayerSource):
                cache[layer['src']] = src
                return src
        if src[-4:].lower() == ".csv":
            mode = _get(layer, 'mode', 'points')
            x_field = _get(layer, 'x', 'lon')
            y_field = _get(layer, 'y', 'lat')
            dialect = _get(layer, 'dialect', 'excel')
            crs = _get(layer, 'crs')
            src = CsvLayer(src, mode=mode, xfield=x_field, yfield=y_field, dialect=dialect, crs=crs)
            return src
        elif src[:8] == "postgis:":
            if 'query' not in layer:
                layer['query'] = 'true'
            if 'table' not in layer:
                raise KartographLayerSourceError('you need to specify a table')
            src = PostGISLayer(src[8:], query=layer['query'], table=layer['table'])
            return src
        else:
            raise KartographLayerSourceError('don\'t know how to handle "' + src + '"')
    elif 'special' in layer:
        if layer['special'] == 'graticule':
            return GraticuleLayer()
        elif layer['special'] == 'sea':
            return SeaLayer()

def _get(layer, prop, default=None):
    if prop in layer:
        return layer[prop]
    return default
