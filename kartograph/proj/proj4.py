
from kartograph.proj.base import Proj
import pyproj


class Proj4(Proj):
    """
    Generic wrapper around Proj.4 projections
    """
    def __init__(self, projstr):
        self.proj = pyproj.Proj(projstr)

    def project(self, lon, lat):
        return self.proj(lon, lat)

    def project_inverse(self, x, y):
        return self.proj(x, y, inverse=True)

    @staticmethod
    def attributes():
        """
        returns array of attribute names of this projection
        """
        return ['projstr']
