"""
geometry utils
"""

def is_clockwise(pts):
	"""
	returns true if a given polygon is in clockwise order
	"""
	s = 0
	for i in range(len(pts)-1):
		if 'x' in pts[i]:
			x1 = pts[i].x
			y1 = pts[i].y
			x2 = pts[i+1].x
			y2 = pts[i+1].y
		else:
			x1, y1 = pts[i]
			x2, y2 = pts[i+1]
		s += (x2-x1) * (y2+y1)
	return s >= 0