

class LayerSource:
	"""
	base class for layer source data providers (e.g. shapefiles)
	"""
	def getFeatures(self, attr, value):
		raise NotImplementedError()
		
		
