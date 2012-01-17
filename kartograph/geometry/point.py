
from geometry import Geometry


class Point(Geometry):
	def __init__(self, x, y):
		self.x = x
		self.y = y
		
	def project(self, proj):
		(x,y) = proj.project(self.x, self.y)
		self.x = x
		self.y = y
		
		
	
	