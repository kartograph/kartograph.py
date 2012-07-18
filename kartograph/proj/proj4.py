
from kartograph.proj.base import Proj
import pyproj


class Proj4(Proj):
    """
    Generic wrapper around Proj.4 projections
    """
    def __init__(self, projstr):
        self.proj = pyproj.Proj(projstr)

    def project(self, lon, lat):
        x, y = self.proj(lon, lat)
        return x, y * -1

    def project_inverse(self, x, y):
        return self.proj(x, y * -1, inverse=True)

    def _visible(self, lon, lat):
        return True

    @staticmethod
    def attributes():
        """
        returns array of attribute names of this projection
        """
        return ['projstr']
