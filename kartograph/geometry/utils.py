"""
geometry utils
"""


def is_clockwise(pts):
    """ returns true if a given linear ring is in clockwise order """
    s = 0
    for i in range(len(pts) - 1):
        if 'x' in pts[i]:
            x1 = pts[i].x
            y1 = pts[i].y
            x2 = pts[i + 1].x
            y2 = pts[i + 1].y
        else:
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
        s += (x2 - x1) * (y2 + y1)
    return s >= 0


def bbox_to_polygon(bbox):
    from shapely.geometry import Polygon
    s = bbox
    poly = Polygon([(s.left, s.bottom), (s.left, s.top), (s.right, s.top), (s.right, s.bottom)])
    return poly


def geom_to_bbox(geom):
    from kartograph.geometry import BBox
    minx, miny, maxx, maxy = geom.bounds
    return BBox(width=maxx - minx, height=maxy - miny, left=minx, top=miny)


def join_features(features, props):
    """ joins polygonal features
    """
    from feature import MultiPolygonFeature

    if len(features) == 0:
        return features

    joined = []
    polygons = []

    for feat in features:
        if isinstance(feat, MultiPolygonFeature):
            polygons.append(feat.geom)
        else:
            joined.append(feat)  # cannot join this

    polygons = filter(lambda x: x is not None, polygons)
    if len(polygons) > 0:
        poly = polygons[0]
        for poly2 in polygons[1:]:
            poly = poly.union(poly2)
        joined.append(MultiPolygonFeature(poly, props))
    return joined
