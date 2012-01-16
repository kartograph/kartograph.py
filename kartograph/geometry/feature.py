

class Feature:
	"""
	feature = geometry + properties
	"""
	def __init__(self, geometry, properties):
		self.geometry = self.geom = geometry
		self.properties = self.props = properties
		
	def __repr__(self):
		return str(self.props)
		
	def project(self, proj):
		self.geometry = self.geometry.project(proj)
		
	def project_view(self, view):
		self.geometry = self.geometry.project_view(view)