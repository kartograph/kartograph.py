
__all__ = ['create_point_store', 'unify_polygon', 'unify_polygons', 'simplify_lines']

from unify import *
from distance import simplify_distance

simplification_methods = dict()
simplification_methods['distance'] = simplify_distance


def simplify_lines(lines, method, params):
    """ simplifies a set of lines """
    simplify = simplification_methods[method]
    for line in lines:
        simplify(line, params)
    return lines
