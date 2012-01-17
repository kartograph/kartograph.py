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
	
	
def bbox_to_polygon(bbox):
	from polygon import MultiPolygon
	s = bbox
	poly = MultiPolygon([[(s.left,s.bottom),(s.left,s.top),(s.right,s.top),(s.right,s.bottom)]])
	return poly	

	
def join_features(features, props):
	from polygon import MultiPolygon
	from feature import Feature
	
	joined = []
	polygons = []
	
	for feat in features:
		if isinstance(feat.geom, MultiPolygon):
			polygons.append(feat.geom)	
		else:
			joined.append(feat) # cannot join this
	
	poly = polygons[0].poly
	for poly2 in polygons[1:]:
		poly = poly | poly2.poly
	joined.append(Feature(MultiPolygon(poly), props))
	return joined