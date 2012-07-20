
from Feature import Feature


class PointFeature(Feature):
    """ wrapper around shapely.geometry.Point """

    def crop_to(self, geometry):
        if self.geometry:
            if self.geometry.is_valid:
                if not self.geometry.intersects(geometry):
                    self.geometry = None
