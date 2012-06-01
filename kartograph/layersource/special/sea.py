
from kartograph.geometry import MultiPolygonFeature
from kartograph.layersource.layersource import LayerSource


class SeaLayer(LayerSource):
    """
    special layer source for grid of longitudes and latitudes (graticule)
    """

    def get_features(self, proj):
        #props = { '__color__':'#d0ddf0' }
        # geom = MultiPolygon(sea_poly)
        geom = proj.bounding_geometry(projected=True)
        return [MultiPolygonFeature(geom, {})]
