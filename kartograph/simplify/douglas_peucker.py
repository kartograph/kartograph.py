

def simplify_douglas_peucker(points, epsilon):
    """
    simplifies a line segment using the Douglas-Peucker algorithm.

    taken from
    http://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm#Pseudocode

    in order to preserve topology of the original polygons the algorithm
    - never removes the first or the last point of a line segment
    - flags all points as simplified after processing (so it won't be processed twice)
    """
    n = len(points)
    kept = []
    if n < 4:
        return points  # skip short lines

    if not points[0].simplified:
        _douglas_peucker(points, 0, n - 1, epsilon)

    return kept
    #print 'kept %d   deleted %d' % (kept, deleted)


def _douglas_peucker(points, start, end, epsilon):
    """ inner part of Douglas-Peucker algorithm, called recursively """
    dmax = 0
    index = 0

    # Find the point with the maximum distance
    for i in range(start + 1, end):
        x1, y1 = points[start]
        x2, y2 = points[end]
        if x1 == x2 and y1 == y2:
            return
        x3, y3 = points[i]
        d = _min_distance(x1, y1, x2, y2, x3, y3)
        if d > dmax:
            index = i
            dmax = d

    # If max distance is greater than epsilon, recursively simplify
    if dmax >= epsilon and start < index < end:
        # recursivly call
        _douglas_peucker(points, start, index, epsilon)
        _douglas_peucker(points, index, end, epsilon)
    else:
        # remove any point but the first and last
        for i in range(start, end + 1):
            points[i].deleted = i == start or i == end
            points[i].simplified = True


def _min_distance(x1, y1, x2, y2, x3, y3):
    """
    the perpendicular distance from a point (x3,y3) to the line from (x1,y1) to (x2,y2)
    taken from http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/
    """
    d = _dist(x1, y1, x2, y2)
    u = (x3 - x1) * (x2 - x1) + (y3 - y1) * (y2 - y1) / (d * d)
    x = x1 + u * (x2 - x1)
    y = y1 + u * (y2 - y1)
    return _dist(x, y, x3, y3)


def _dist(x1, y1, x2, y2):
    """ eucledian distance between two points """
    import math
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)
