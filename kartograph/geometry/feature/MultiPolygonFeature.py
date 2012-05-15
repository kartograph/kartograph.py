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
        print self.props['FIPS_1'],
        rings = []
        num_holes = []
        for polygon in self.geometry.geoms:
            num_holes.append(len(polygon.interiors))  # store number of holes per polygon
            ext = polygon.exterior.coords
            rings.append(ext)
            print len(ext),
            for hole in polygon.interiors:
                rings.append(hole.coords)
        print '\t %d polygons\t %d rings\t %d holes' % (len(num_holes), len(rings), sum(num_holes))
        self._topology_rings = unify_rings(rings, point_store, precision=precision, feature=self)
        self._topology_num_holes = num_holes

    def break_into_lines(self):
        """
        temporarily stores the geometry in a custom representation in order
        to preserve topology during simplification
        """
        # print '\n\n', self.props['NAME_1'],
        lines = []
        lines_per_ring = []
        for ring in self._topology_rings:
            l = 0  # store number of lines per ring
            s = 0
            i = s + 1
            K = len(ring)
            # print '\n\tnew ring (' + str(K) + ')',
            # find first break-point
            while i < K and ring[i].features == ring[i - 1].features:
                i += 1
            if i == len(ring):  # no break-point found at all
                line = ring  # so the entire ring is treated as one line
                # print len(line),
                lines.append(line)  # store it
                lines_per_ring.append(1)  # and remember that this ring has only 1 line
                continue  # proceed to next ring
            s = i  # store index of first break-point
            a = None
            # loop-entry conditions:
            # - 'a' holds the index of the break-point, equals to s
            # - 's' is the index of the first break-point in the entire ring
            while a != s:
                if a is None:
                    a = s  # if no break-point is set, start with the first one
                line = [a]  # add starting brak-point to line
                i = a + 1  # proceed to next point
                if i == K:
                    i = 0  # wrap around to first point if needed
                while i != s and ring[i].features == ring[((i - 1) + len(ring)) % len(ring)].features:  # look for end of this line
                    line.append(i)  # add point to line
                    i += 1  # proceed to next point
                    if i == K:
                        i = 0  # eventually wrap around
                if i != s:
                    line.append(i)  # add end point to line
                l += 1  # increase line-per-ring counter
                a = i  # set end point as next starting point
                #if a == s:  # if next starting point is the first break point..
                #    line.append(s)  # append
                # print len(line),
                for ll in range(len(line)):
                    line[ll] = ring[line[ll]]  # replace point indices with actual points
                lines.append(line)  # store line
            lines_per_ring.append(l)

        self._topology_lines_per_ring = lines_per_ring
        return lines

    def restore_geometry(self, lines):
        """
        restores geometry from linear rings
        """
        from shapely.geometry import Polygon, MultiPolygon
        print self.props['FIPS_1'],
        # at first we restore the rings
        rings = []
        p = 0
        for l in self._topology_lines_per_ring:
            ring = []
            for k in range(p, p + l):
                line = []
                for pt in lines[k]:
                    if not pt.deleted:
                        line.append((pt[0], pt[1]))
                ring += line
            p += l
            rings.append(ring)
        # then we restore polygons from rings
        ring_iter = iter(rings)
        polygons = []
        holes_total = 0
        for num_hole in self._topology_num_holes:
            ext = ring_iter.next()
            print len(ext),
            holes = []
            while num_hole > 0:
                hole = ring_iter.next()
                if len(hole) > 3:
                    holes.append(hole)
                holes_total += 1
                num_hole -= 1
            if len(ext) > 3:
                polygons.append(Polygon(ext, holes))
        print '\t %d polygons \t %d rings \t %d holes' % (len(polygons), len(rings), holes_total)
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
