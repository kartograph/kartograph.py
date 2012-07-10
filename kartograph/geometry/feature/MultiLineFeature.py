from Feature import Feature
from kartograph.simplify.unify import unify_rings
import shapely.wkt


class MultiLineFeature(Feature):
    """ wrapper around shapely.geometry.LineString """

    def __repr__(self):
        return 'MultiLineFeature(' + str(len(self.geometry.coords)) + ' pts)'

    def project_geometry(self, proj):
        """ project the geometry """
        self.geometry = proj.plot(self.geometry)

    def compute_topology(self, point_store, precision=None):
        """
        converts the MultiLine geometry into a set of linear rings
        and 'unifies' the points in the rings in order to compute topology
        """
        rings = []
        for line in self._geoms:
            rings.append(line.coords)
        self._topology_rings = unify_rings(rings, point_store, precision=precision, feature=self)

    def break_into_lines(self):
        """
        temporarily stores the geometry in a custom representation in order
        to preserve topology during simplification
        """
        return self._topology_rings

    def restore_geometry(self, lines, minArea=0):
        """
        restores geometry from linear rings
        """
        from shapely.geometry import LineString, MultiLineString
        linestrings = []
        for line in lines:
            linestrings.append(LineString(line))

        if len(linestrings) > 0:
            self.geometry = MultiLineString(linestrings)
        else:
            self.geometry = None

    @property
    def _geoms(self):
        """ returns a list of geoms """
        return hasattr(self.geometry, 'geoms') and self.geometry.geoms or [self.geometry]
