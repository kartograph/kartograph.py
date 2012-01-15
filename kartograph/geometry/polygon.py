
from geometry import *



class Polygon(SolidGeometry):

	def __init__(self, points):
		self.points = points

	def area(self):
		if self.__area is not None:
			return self.__area
		a = 0
		pts = self.points
		for i in range(len(pts)-1):
			p0 = pts[i]
			p1 = pts[i+1]
			a += p0.x*p1.y - p1.x*p0.y
		self.__area = abs(a)*.5
		return self.__area
		
	def project(self, proj):
		self.invalidate()
		self.points = proj.plot(self.points)



class ComplexPolygon(SolidGeometry):
	"""
	A simple polygon with non intersecting holes
	the first contour is the polygon and every following contour is a hole
	"""
	def __init__(self, contours):
		self.polygon = Polygon(contours[0])
		self.holes = []
		for i in range(1, len(contours):
			self.holes.append(Polygon(contours[1]))

	def area(self):
		if self.__area is not None:
			return self.__area
		a = self.polygon.area()
		for hole in self.holes:
			a -= hole.area()
		self.__area = a
		return self.__area
		
		
class MultiPolygon(SolidGeometry):
	"""
	Several complex polygons
	"""
	def __init__(self, polygons):
		self.polygons = polygons

	def area(self):
		if self.__area is not None:
			return self.__area
		a = 0
		for poly in self.polygons:
			a += poly.area()
		self.__area = a
		return self.__area
		
