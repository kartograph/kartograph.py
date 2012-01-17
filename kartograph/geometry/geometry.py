

		
class Geometry:
	"""
	base class for all geometry
	"""
	def project(self, proj):
		"""
		project geometry
		"""
		raise NotImplementedError('project() is not implemented')
	
	def bbox(self):
		raise NotImplementedError('bbox() is not implemented')
	
	def project(self, proj):
		raise NotImplementedError('project() is not implemented')
	
	def project_view(self, view):
		raise NotImplementedError('project_view() is not implemented')
		
	def to_svg(self, round=0):
		raise NotImplementedError('to_svg() is not implemented')
		
	def crop_to(self, view_bounds):
		raise NotImplementedError('crop_to() is not implemented')

	def substract_geom(self, geom):
		raise NotImplementedError('substract_geom() is not implemented yet')
		
	def is_emtpy(self):
		return False
		
	def unify(self, point_store):
		raise NotImplementedError('unify() is not implemented yet')
		
	def points(self):
		"""
		returns a list of point lists
		"""
		raise NotImplementedError('points() is not implemented yet')

	
class SolidGeometry(Geometry):
	"""
	base class for all solid geometry, e.g. polygons
	"""
	def area():
		"""
		calculates area for this geometry
		"""
		raise NotImplementedError('area() is not implemented')
		
	def centroid():
		"""
		calculates centroid for this geometry
		"""
		raise NotImplementedError('centroid() is not implemented')
	
	def invalidate(self):
		self.__area = None