
__all__ = ['create_point_store', 'unify_polygon', 'unify_polygons', 'simplify_lines']

from unify import *
from distance import simplify_distance
from douglas_peucker import simplify_douglas_peucker
from visvalingam import simplify_visvalingam_whyatt


simplification_methods = dict()
simplification_methods['distance'] = simplify_distance
simplification_methods['douglas-peucker'] = simplify_douglas_peucker
simplification_methods['visvalingam-whyatt'] = simplify_visvalingam_whyatt


def simplify_lines(lines, method, params):
    """ simplifies a set of lines """
    simplify = simplification_methods[method]
    out = []
    for line in lines:
        # remove duplicate points from line
        unique = [line[0]]
        for i in range(1, len(line)):
            if line[i] != line[i - 1]:
                unique.append(line[i])
        simplify(unique, params)
        out.append(unique)
    return out
