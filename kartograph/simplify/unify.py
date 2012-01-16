

def unify(polygons):
	"""
	Replaces duplicate points with an instance of the 
	same point
	"""
	point_store = {}
	out_polygons = []
	kept = 0
	removed = 0
	for poly in polygons:
		new_points = []
		for pt in poly.points:
			pid = '%f-%f' % (pt.x, pt.y)
			if pid in point_store:
				point = point_store[pid]
				if point.two: point.three = True
				else: point.two = True
				removed += 1
			else:
				point = pt
				kept += 1
				point_store[pid] = pt
			new_points.append(point)
		poly.points = new_points
	#print 'unifying polygons removed %d duplicate points (of %d total points)'%(removed, removed+kept)			

