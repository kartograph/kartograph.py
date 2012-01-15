

class Feature:
	"""
	feature = geometry + properties
	"""
	def __init__(self, geometry, properties):
		self.geometry = geometry
		self.properties = self.props = properties
		
		