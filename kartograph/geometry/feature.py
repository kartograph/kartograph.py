
from kartograph import errors

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
		self.geometry = self.geom = self.geometry.project(proj)
		
	def project_view(self, view):
		self.geometry = self.geom = self.geometry.project_view(view)
	
	def crop_to(self, view_bounds):
		self.geometry = self.geom = self.geometry.crop_to(view_bounds)
		
	def substract_geom(self, geom):
		self.geometry = self.geom = self.geometry.substract_geom(geom)
		
	def to_svg(self, round, attributes=[]):
		svg = self.geometry.to_svg(round)
		# todo: add data attribtes
		for cfg in attributes:
			if cfg['src'] not in self.props:
				raise errors.KartographError(('attribute not found "%s"'%cfg['src']))
			svg['data-'+cfg['tgt']] = self.props[cfg['src']]
		if '__color__' in self.props:
			svg['fill'] = self.props['__color__']
		return svg
		
	def is_empty(self):
		return self.geom.is_empty()