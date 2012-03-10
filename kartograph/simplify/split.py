### split polygons into a set of line segments ###


def simplify_features(features, algorithm='distance', parameters={}):
    """ simplifies geometry of the given features """
    for feature in features:
        geom = feature.geometry
        lines = geom.line_segments()


def geometry_to_line_segments(geom):


class Line(object):
    id = 0
    points = []


class Polygon(object):
    line_segments = []