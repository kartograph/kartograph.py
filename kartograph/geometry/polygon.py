
from geometry import *
from bbox import BBox
import utils


class Polygon(SolidGeometry):

	def __init__(self, points):
		self.__area = None
		self.__centroid = None
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

		
		
class MultiPolygon(SolidGeometry):
	"""
	Several complex polygons
	"""
	def __init__(self, contours):
		self.__area = None
		self.__areas = None
		self.__centroid = None
		self.contours = contours
		from Polygon import Polygon as GPCPoly
		poly = GPCPoly()
		for pts in contours:
			ishole = utils.is_clockwise(pts)
			poly.addContour(pts, ishole)
		self.poly = poly

	def area(self):
		if self.__area is not None:
			return self.__area
		self.__area = self.poly.area()
		return self.__area
	
	
	def areas(self):
		"""
		returns array of areas of all sub-polygons
		areas of holes are < 0
		"""
		if self.__areas is not None:
			return self.__areas
		a = []
		for i in range(len(self.poly)):
			t = self.poly.area(i)
			if self.poly.isHole(i): t *= -1
			a.append(t)
		self.__areas = a
		return a
	
	
	def centroid(self):
		"""
		returns the center of gravity for this polygon
		"""
		if self.__centroid is not None:
			return self.__centroid
		self.__centroid = self.poly.center()
		return self.__centroid
	
	
	def bbox(self, min_area = 0):
		"""
		smart bounding box
		"""
		bb = []
		bbox = BBox()
		if min_area == 0:
			bb.append(self.poly.boundingBox())
		else:
			areas = self.areas()
			max_a = max(areas)
			for i in range(len(self.poly)):
				if self.poly.isHole(i): continue
				a = areas[i]
				if a < max_a * min_area: continue
				bb.append(self.poly.boundingBox(i))
		for b in bb:
			bbox.update((b[0],b[2]))
			bbox.update((b[1],b[2]))
			bbox.update((b[0],b[3]))
			bbox.update((b[1],b[3]))
		return bbox
	
	
	def project(self, proj):
		"""
		returns a new multi-polygon whose contours are
		projected to a map projection
		"""
		in_contours = self.contours
		out_contours = []
		for pts in in_contours:
			out_contours += proj.plot(pts)
		out_poly = MultiPolygon(out_contours)
		return out_poly
		
		
	def project_view(self, view):
		"""
		returns a new multi-polygon whose contours are 
		projected to a new view
		"""
		in_poly = self
		contours = in_poly.contours
		out = []
		for contour in contours:
			out_c = []
			for pt in contour:
				pt = view.project(pt)
				out_c.append(pt)
			out.append(out_c)
		out_poly = MultiPolygon(out)
		return out_poly	
	
	
	def to_svg(self, round):
		"""
		constructs a svg representation of this polygon
		"""
		from svgfig import SVG
		path_str = ""
		if round is False: fmt = '%f,%f'
		else: 
			fmt = '%.'+str(round)+'f'
			fmt = fmt+','+fmt
			
		for pts in self.contours:
			cont_str = ""
			for pt in pts:
				if cont_str == "": cont_str = "M"
				else: cont_str += "L"
				cont_str += fmt % pt
			cont_str += "Z "
			path_str += cont_str
			
		path = SVG('path', d=path_str)
		return path

	