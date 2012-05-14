

def simplify_distance(points, dist):
    """
    simplifies a line segment using a very simple algorithm that checks the distance
    to the last non-deleted point. the algorithm operates on line segments.

    in order to preserve topology of the original polygons the algorithm
    - never removes the first or the last point of a line segment
    - flags all points as simplified after processing (so it won't be processed twice)
    """
    dist_sq = dist * dist
    n = len(points)

    kept = []
    deleted = 0
    if n < 4:
        return points

    for i in range(0, n):
        pt = points[i]
        if i == 0 or i == n - 1:
            # never remove first or last point of line
            pt.simplified = True
            lpt = pt
            kept.append(pt)
        else:
            d = (pt.x - lpt.x) * (pt.x - lpt.x) + (pt.y - lpt.y) * (pt.y - lpt.y)  # compute distance to last point
            if pt.simplified or d > dist_sq:  # if point already handled or distance exceeds threshold..
                kept.append(pt)  # ..keep the point
                lpt = pt
            else:  # otherwise remove it
                deleted += 1
                pt.deleted = True
            pt.simplified = True

    if len(kept) < 4:
        for pt in points:
            pt.deleted = False
        return points

    return kept
    #print 'kept %d   deleted %d' % (kept, deleted)
