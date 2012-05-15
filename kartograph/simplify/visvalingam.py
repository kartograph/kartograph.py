

def simplify_visvalingam_whyatt(points, tolerance):
    """ Visvalingam-Whyatt simplification """
    if points[0].simplified:
        return
    if len(points) < 3:
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
            if pts[i - 1] in preserved or pts[i + 1] in preserved:
                # the current segment is too close to a previously-preserved one.
                continue

            popped.append(i)

            preserved.add(pts[i - 1])
            preserved.add(pts[i + 1])

        if len(popped) == 0:
            # no points removed, so break out of loop
            break

        for i in popped:
            # remove popped indices from pts list
            points[pts[i]].deleted = True
        for i in popped:
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
