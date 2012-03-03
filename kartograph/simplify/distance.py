
def simplify_distance(points, dist):
    """
    Simplifies a list of points
    """
    new_points = []
    dist_sq = dist*dist
    n = len(points)
    
    kept = 0
    deleted = 0
    
    for i in range(0, n):
        # look for the first "inner" points and mark them as not deletable
        j = (i+1)%n
        pt = points[i]
        npt = points[j]
        if pt.two and not npt.two:
            pt.keep = True
        if not pt.two and npt.two:
            npt.keep = True
    
    for i in range(0, n):
        pt = points[i]
        if i == 0 or i == n-1:
            pt.simplified = True
            lpt = pt
        else:
            d = (pt.x - lpt.x) * (pt.x - lpt.x) + (pt.y - lpt.y) * (pt.y - lpt.y)
            if d > dist_sq or not pt.isDeletable():
                lpt = pt
                kept += 1
            else:
                pt.deleted = True
                deleted += 1
            pt.simplified = True
            
    #print 'kept %d   deleted %d' % (kept, deleted)
    
    