
from options import parse_options
from layersource import handle_layer_source
from errors import *

class Kartograph(object):
	"""
	main class of Kartograph
	"""
	def __init__(self):
		pass
		
	def generate(self, opts, outfile=None):
		"""
		generates svg map
		"""
		parse_options(opts)
		self.prepare_layers(opts)
		lon0,lat0 = self.get_map_center(opts)
		print lon0,lat0
		# print opts	
		
			
	def prepare_layers(self, opts):
		"""
		prepares layer sources
		"""
		self.layers = layers = {}
		for layer in opts['layers']:
			id = layer['id']
			src = handle_layer_source(layer['src'])
			layers[id] = src
			
					
	def get_map_center(self, opts):
		"""
		depends on the bounds config
		"""
		mode = opts['bounds']['mode']
		data = opts['bounds']['data']
		if mode == 'bbox':
			lon0 = data[0] + 0.5 * (data[2] - data[0])
			lat0 = data[1] + 0.5 * (data[3] - data[1])
		elif mode == 'points':
			lon0 = 0
			lat0 = 0
			m = 1/len(data)
			for (lon,lat) in data:
				lon0 += m*lon
				lat0 += m*lat
		elif mode == 'polygons':
			features = []
			id = data['layer']
			if id not in self.layers:
				raise KartographError('layer not found "%s"'%id)
			layer = self.layers[id]
			attr = data['attribute']
			values = data['values']
			features = []
			for val in values:
				features += layer.getFeatures(attr, val)
			print features
			
		return (lon0,lat0)
		

	
	
	def get_bounds(self, opts, proj):
		"""
		computes the (x,y) bounding box for the map, given a specific projection
		"""
		bnds = opts['bounds']
		type = bnds['type']
		data = bnds['data']
		
		if bt == "bbox": # catch special case bbox
			bt = "points"
			lon0,lat0,lon1,lat1 = data # lon0,lat0,lon1,lat1
			data = [(lon0,lat0),(lon0,lat1),(lon1,lat0),(lon1,lat1)]
		
		bbox = Bounds2D()
				
		if bt == "points":
			for lon,lat in data:
				pt = proj.project(lon,lat)
				bbox.update(pt)
				
		if bt == "polygons":
			data['layer'] = 'countries'
			data['idcol'] = 'ISO3'
			data['ids'] = ['DEU','FRA','ESP']
			
		
		return bbox
	
