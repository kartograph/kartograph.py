
from kartograph import errors
import re

class Feature:
	"""
	feature = geometry + properties
	"""
	def __init__(self, geometry, properties):
		self.geometry = self.geom = geometry
		self.properties = self.props = properties
		
	def __repr__(self):
		return 'Feature()'
		
	def project(self, proj):
		self.geometry = self.geom = self.geometry.project(proj)
		
	def project_view(self, view):
		self.geometry = self.geom = self.geometry.project_view(view)
	
	def crop_to(self, view_bounds):
		self.geometry = self.geom = self.geometry.crop_to(view_bounds)
		
	def substract_geom(self, geom):
		self.geometry = self.geom = self.geometry.substract_geom(geom)
		
	def to_svg(self, round, attributes=[], styles=None):
		svg = self.geometry.to_svg(round)
		if svg is None:
			return None
		# todo: add data attribtes
		for cfg in attributes:
			if 'src' in cfg:
				tgt = re.sub('(\W|_)+', '-', cfg['tgt'].lower())
				if cfg['src'] not in self.props:
					continue
					#raise errors.KartographError(('attribute not found "%s"'%cfg['src']))
				val = self.props[cfg['src']]
				import unicodedata
				if isinstance(val, str):
					val = unicode(val, errors='ignore')
					val = unicodedata.normalize('NFKD', val).encode('ascii','ignore')				
				svg['data-'+tgt] = val
				
			elif 'where' in cfg:
				# can be used to replace attributes...
				src = cfg['where']
				tgt = cfg['set']
				if len(cfg['equals']) != len(cfg['to']):
					raise errors.KartographError('attributes: "equals" and "to" arrays must be of same length')
				for i in range(len(cfg['equals'])):
					if self.props[src] == cfg['equals'][i]:	
						svg['data-'+tgt] = cfg['to'][i]
				
		if '__color__' in self.props:
			svg['fill'] = self.props['__color__']
		return svg
		
	def to_kml(self, round, attributes=[]):
		path = self.geometry.to_kml(round)
		from pykml.factory import KML_ElementMaker as KML
		
		pm = KML.Placemark(
			KML.name(self.props[attributes[0]['src']]),
			path
		)
		
		xt = KML.ExtendedData()
		
		for cfg in attributes:
			if 'src' in cfg:
				if cfg['src'] not in self.props:
					continue
					#raise errors.KartographError(('attribute not found "%s"'%cfg['src']))
				val = self.props[cfg['src']]
				import unicodedata
				if isinstance(val, str):
					val = unicode(val, errors='ignore')
					val = unicodedata.normalize('NFKD', val).encode('ascii','ignore')				
				xt.append(KML.Data(
					KML.value(val),
					name=cfg['tgt']
				))
			elif 'where' in cfg:
				src = cfg['where']
				tgt = cfg['set']
				if len(cfg['equals']) != len(cfg['to']):
					raise errors.KartographError('attributes: "equals" and "to" arrays must be of same length')
				for i in range(len(cfg['equals'])):
					if self.props[src] == cfg['equals'][i]:	
						#svg['data-'+tgt] = cfg['to'][i]
						xt.append(KML.Data(
							KML.value(cfg['to'][i]),
							name=tgt
						))
		pm.append(xt)		
		
		return pm
		
	def is_empty(self):
		return self.geom.is_empty()