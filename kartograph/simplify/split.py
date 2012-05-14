### split polygons into a set of line segments ###

from sqlite3 import connect


def simplify_features(features, algorithm='distance', parameters={}):
    """ simplifies geometry of the given features """
    for feature in features:
        geom = feature.geometry
        lines = geom.line_segments()


def geometry_to_line_segments(geom):


def compute_topology(features):
    """ computes a topology of a set of polygon features """
    db = connect(':memory:').cursor()



class Line(object):
    id = 0
    points = []


class Polygon(object):
    line_segments = []