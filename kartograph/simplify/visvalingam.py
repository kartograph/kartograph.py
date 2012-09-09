

def simplify_visvalingam_whyatt(points, tolerance):
    """ Visvalingam-Whyatt simplification
    implementation borrowed from @migurski:
    https://github.com/migurski/Bloch/blob/master/Bloch/__init__.py#L133
    """
    if len(points) < 3:
        return
    if points[1].simplified:
        return

    min_area = tolerance ** 2

    pts = range(len(points))  # pts stores an index of all non-deleted points

    while len(pts) > 4:
        preserved, popped = set(), []
        areas = []

        for i in range(1, len(pts) - 1):
            x1, y1 = points[pts[i - 1]]
            x2, y2 = points[pts[i]]
            x3, y3 = points[pts[i + 1]]
            # compute and store triangle area
            areas.append((_tri_area(x1, y1, x2, y2, x3, y3), i))

        areas = sorted(areas)

        if not areas or areas[0][0] > min_area:
            # there's nothing to be done
            for pt in points:
                pt.simplified = True
            break

        # Reduce any segments that makes a triangle whose area is below
        # the minimum threshold, starting with the smallest and working up.
        # Mark segments to be preserved until the next iteration.

        for (area, i) in areas:

            if area > min_area:
                # there won't be any more points to remove.
                break

            if i - 1 in preserved or i + 1 in preserved:
                # the current segment is too close to a previously-preserved one.
                #print "-pre", preserved
                continue

            points[pts[i]].deleted = True
            popped.append(i)

            # make sure that the adjacent points
            preserved.add(i - 1)
            preserved.add(i + 1)

        if len(popped) == 0:
            # no points removed, so break out of loop
            break

        popped = sorted(popped, reverse=True)
        for i in popped:
            # remove point from index list
            pts = pts[:i] + pts[i + 1:]

    for pt in points:
        pt.simplified = True


def _tri_area(x1, y1, x2, y2, x3, y3):
    """
    computes the area of a triangle given by three points
    implementation taken from:
    http://www.btinternet.com/~se16/hgb/triangle.htm
    """
    return abs((x2*y1-x1*y2)+(x3*y2-x2*y3)+(x1*y3-x3*y1))/2.0
