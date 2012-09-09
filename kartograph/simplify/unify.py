
from mpoint import MPoint

"""
the whole point of the unification step is to convert all points into unique MPoint instances
"""


def create_point_store():
    """ creates a new point_store """
    point_store = {'kept': 0, 'removed': 0}
    return point_store


def unify_rings(rings, point_store, precision=None, feature=None):
    out = []
    for ring in rings:
        out.append(unify_ring(ring, point_store, precision=precision, feature=feature))
    return out


def unify_ring(ring, point_store, precision=None, feature=None):
    """
    Replaces duplicate points with MPoint instances
    """
    out_ring = []
    lptid = ''
    for pt in ring:
        if 'deleted' not in pt:
            pt = MPoint(pt[0], pt[1])  # eventually convert to MPoint
        # generate hash for point
        if precision is not None:
            fmt = '%' + precision + 'f-%' + precision + 'f'
        else:
            fmt = '%f-%f'
        pid = fmt % (pt.x, pt.y)
        if pid == lptid:
            continue  # skip double points
        lptid = pid
        if pid in point_store:
            # load existing point from point store
            point = point_store[pid]
            point_store['removed'] += 1
        else:
            point = pt
            point_store['kept'] += 1
            point_store[pid] = pt

        point.features.add(feature)
        out_ring.append(point)
    return out_ring
