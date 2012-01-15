

		
class Geometry:
	"""
	base class for all geometry
	"""
	def project(self, proj):
		"""
		project geometry
		"""
		raise NotImplementedError('project() is not implemented')
	

	
class SolidGeometry(Geometry):
	"""
	base class for all solid geometry, e.g. polygons
	"""
	def area():
		"""
		calculates area for this geometry
		"""
		raise NotImplementedError('area() is not implemented')
		
	def invalidate(self):
		self.__area = None