

class LayerSource:
	"""
	base class for layer source data providers (e.g. shapefiles)
	"""
	def get_features(self, filter=None):
		raise NotImplementedError()
		
		
