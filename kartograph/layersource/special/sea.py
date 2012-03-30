
from kartograph.geometry import Line, Feature, MultiPolygon
from kartograph.layersource.layersource import LayerSource

class SeaLayer(LayerSource):
    """
    special layer source for grid of longitudes and latitudes (graticule)
    """

    def get_features(self, sea_poly):
        #props = { '__color__':'#d0ddf0' }
        geom = MultiPolygon(sea_poly)
        return [Feature(geom, {})]
