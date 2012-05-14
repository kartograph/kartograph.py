from Feature import Feature
from kartograph.errors import KartographError
from kartograph.simplify.unify import unify_rings


class MultiPolygonFeature(Feature):
    """ wrapper around shapely.geometry.MultiPolygon """

    def __repr__(self):
        return 'MultiPolygonFeature()'

    def geometry_to_svg(self, svg, round):
        """ constructs a svg representation of this polygon """
        path_str = ""
        if round is False:
            fmt = '%f,%f'
        else:
            fmt = '%.' + str(round) + 'f'
            fmt = fmt + ',' + fmt
        for polygon in self.geometry.geoms:
            for ring in [polygon.exterior] + polygon.interiors:
                cont_str = ""
                kept = []
                for pt in ring.coords:
                    kept.append(pt)
                if len(kept) <= 3:
                    continue
                for pt in kept:
                    if cont_str == "":
                        cont_str = "M"
                    else:
                        cont_str += "L"
                    cont_str += fmt % pt
                cont_str += "Z "
                path_str += cont_str
            if path_str == "":
                return None
            path = svg.node('path', d=path_str)
            return path

    def project_geometry(self, proj):
        """ project the geometry """
        from shapely.geometry import MultiPolygon
        polygons = self.geometry.geoms
        projected = []
        for polygon in polygons:
            projected += _project_polygon(polygon, proj)
        self.geometry = MultiPolygon(projected)

    def compute_topology(self, point_store, precision=None):
        """
        converts the MultiPolygon geometry into a set of linear rings
        and 'unifies' the points in the rings in order to compute topology
        """
        rings = []
        num_holes = []
        for polygon in self.geometry.geoms:
            num_holes.append(len(polygon.interiors))  # store number of holes per polygon
            rings.append(polygon.exterior.coords)
            for hole in polygon.interiors:
                rings.append(hole.coords)
        self._topology_rings = unify_rings(rings, point_store, precision=precision, feature=self)
        self._topology_num_holes = num_holes

    def break_into_lines(self):
        """
        temporarily stores the geometry in a custom representation in order
        to preserve topology during simplification
        """
        lines = []
        lines_per_ring = []
        for ring in self._topology_rings:
            l = 0  # store number of lines per ring
            s = 0
            i = s + 1
            # find first break-point
            while ring[i].features == ring[i - 1].features and i < len(ring):
                i += 1
            s = i  # store index of first break-point
            a = s + 1  # start round-trip at next point
            while a != s:
                line = [a]  # add start point to line
                i = a + 1  # proceed to next point
                while i != s and ring[i].features == ring[i - 1].features:  # look for end of next line
                    line.append(i)  # add point to line
                    i += 1
                    if i == len(ring):
                        i = 0  # flip to beginning
                line.append(i)  # add end point to line
                print line
                for ll in range(len(line)):
                    line[ll] = ring[ll]  # replace point indices with actual points
                lines.append(line)  # store line
                l += 1  # increase line-per-ring counter
                a = i
            lines_per_ring.append(l)

        self._topology_lines_per_ring = lines_per_ring
        return lines

    def restore_geometry(self, lines):
        """
        restores geometry from linear rings
        """
        from shapely.geometry import Polygon, MultiPolygon
        # at first we restore the rings
        rings = []
        for l in self._topology_lines_per_ring:
            ring = []
            for k in range(l):
                line = lines[k]
                ring += line[:-1]
            rings.append(ring)
        # then we restore polygons from rings
        ring_iter = iter(rings)
        polygons = []
        for num_hole in self._topology_num_holes:
            ext = ring_iter.next()
            holes = []
            while num_hole > 0:
                holes.append(ring_iter.next())
                num_hole -= 1
            polygons.append(Polygon(ext, holes))
        self.geometry = MultiPolygon(polygons)


def _project_polygon(polygon, proj):
    """ project a shapely.geometry.Polygon
    returns array of shapely.geometry.Polygon instances
    """
    from shapely.geometry import Polygon
    exterior = polygon.exterior
    interiors = polygon.interiors
    out_ext = _project_contours([exterior], proj)
    out_int = _project_contours(interiors, proj)
    if len(out_ext) == 0:
        return []
    elif len(out_ext) == 1:
        return [Polygon(out_ext[0], out_int)]
    elif len(out_ext) > 1 and len(out_int) == 0:
        res = []
        for ext in out_ext:
            res.append(Polygon(ext))
    else:
        raise NotImplementedError('not implemented: a polygon with holes was split during map projection')


def _project_contours(contours, proj):
    out = []
    for ring in contours:
        pcont = proj.plot(ring.coords)
        if pcont != None:
            out += pcont
    return out
