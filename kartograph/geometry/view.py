
from polygon import MultiPolygon
from point import Point

class View(object):
	"""
	translates a point to a view
	"""
	def __init__(self, bbox=None, width=None, height=None, padding=0):
		self.bbox = bbox
		self.width = width
		self.padding = padding
		self.height = height
		if bbox:
			self.scale = min((width-padding*2) / bbox.width, (height-padding*2) / bbox.height)
	
	
	def project(self, pt):
		bbox = self.bbox
		if not bbox:
			return pt
		s = self.scale
		h = self.height
		w = self.width
		if isinstance(pt, Point):
			px = pt.x
			py = pt.y
		else:
			px = pt[0]
			py = pt[1]
		x = (px - bbox.left) * s + (w - bbox.width * s) * .5
		y = (py - bbox.top) * s + (h - bbox.height * s) * .5
		return ((x,y), Point(x, y))[isinstance(pt, Point)]
	
	
	def __str__(self):
		return 'View(w=%f, h=%f, pad=%f, scale=%f, bbox=%s)' % (self.width, self.height, self.padding, self.scale, self.bbox)
