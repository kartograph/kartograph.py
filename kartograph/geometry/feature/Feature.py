from shapely.geos import TopologicalError
import sys

verbose = False

# # Feature
# Base class for map features. Each feature has a geometry (shapely.geometry.*)
# and a property dictionary


class Feature:
    def __init__(self, geometry, properties):
        self.geometry = geometry
        self.properties = properties

    def __repr__(self):
        return 'Feature(' + self.geometry.__class__.__name__ + ')'

    def project(self, proj):
        self.project_geometry(proj)

    def unify(self, point_store, precision=None):
        from kartograph.simplify import unify_polygons
        contours = self.contours
        contours = unify_polygons(contours, point_store, precision)
        self.apply_contours(contours)

    def project_view(self, view):
        if self.geometry:
            self.geometry = view.project_geometry(self.geometry)

    def crop_to(self, geometry):
        if self.geometry:
            if self.geometry.is_valid and geometry.is_valid:
                if self.geometry.intersects(geometry):
                    try:
                        self.geometry = self.geometry.intersection(geometry)
                    except TopologicalError:
                        self.geometry = None
                else:
                    self.geometry = None
            else:
                if verbose:
                    sys.stderr.write("warning: geometry is invalid")


    def subtract_geom(self, geom):
        if self.geometry:
            try:
                self.geometry = self.geometry.difference(geom)
            except TopologicalError:
                if verbose:
                    sys.stderr.write('warning: couldnt subtract from geometry')

    def project_geometry(self, proj):
        self.geometry = proj.plot(self.geometry)

    def is_empty(self):
        return self.geom is not None

    def is_simplifyable(self):
        return False

    @property
    def geom(self):
        return self.geometry

    @property
    def props(self):
        return self.properties
