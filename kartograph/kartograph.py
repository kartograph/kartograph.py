
from options import parse_options
from layersource import handle_layer_source
from geometry import SolidGeometry, BBox, MultiPolygon, View
from proj import projections
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
		
		proj = self.get_projection(opts)
		bounds_poly = self.get_bounds(opts,proj)
		bbox = bounds_poly.bbox()
		view = self.get_view(opts, bbox)
		view_bounds = bounds_poly.project_view(view)
		
		for layer in opts['layers']:
			features = self.get_features(layer, proj, view)
			
		print features
		
		
		
	
	def prepare_layers(self, opts):
		"""
		prepares layer sources
		"""
		self.layers = layers = {}
		for layer in opts['layers']:
			id = layer['id']
			src = handle_layer_source(layer['src'])
			layers[id] = src

	
	def get_projection(self, opts):
		"""
		instanciates the map projection
		"""
		map_center = self.get_map_center(opts)
		projC = projections[opts['proj']['id']]
		p_opts = {}
		for prop in opts['proj']:
			if prop != "id":
				p_opts[prop] = opts['proj'][prop]
			if prop == "lon0" and p_opts[prop] == "auto":
				p_opts[prop] = map_center[0]
			elif prop == "lat0" and p_opts[prop] == "auto":
				p_opts[prop] = map_center[1]		
		proj = projC(**p_opts)
		return proj
		
					
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
			features = self.get_bounds_polygons(opts)
			if isinstance(features[0].geom, SolidGeometry):
				(lon0, lat0) = features[0].geom.centroid()
		return (lon0,lat0)
				

	def get_bounds(self, opts, proj):
		"""
		computes the (x,y) bounding box for the map, 
		given a specific projection
		"""
		from geometry.utils import bbox_to_polygon
		
		bnds = opts['bounds']
		mode = bnds['mode'][:]
		data = bnds['data']
		
		if mode == "bbox": # catch special case bbox
			lon0,lat0,lon1,lat1 = data # lon0,lat0,lon1,lat1
			pts = [(lon0,lat0),(lon0,lat1),(lon1,lat0),(lon1,lat1)]
			contours = proj.plot(pts)
			return MultiPolygon(contours)
		
		bbox = BBox()
				
		if mode == "points":
			for lon,lat in data:
				pt = proj.project(lon,lat)
				bbox.update(pt)
				
		if mode == "polygons":
			features = self.get_bounds_polygons(opts)
			for feature in features:
				fbbox = feature.geom.project(proj).bbox(data["min_area"])
				bbox.join(fbbox)
		
		return bbox_to_polygon(bbox)
	
	
	def get_bounds_polygons(self, opts):
		"""
		for bounds mode "polygons" this helper function
		returns a list of all polygons that the map should
		be cropped to
		"""
		features = []
		data = opts['bounds']['data']
		id = data['layer']
		if id not in self.layers:
			raise KartographError('layer not found "%s"'%id)
		layer = self.layers[id]
		attr = data['attribute']
		values = data['values']
		features = layer.get_features(attr, lambda id: id in values)
		return features


	def get_view(self, opts, bbox):
		"""
		returns the output view
		"""
		exp = opts["export"]
		w = exp["width"]
		h = exp["height"]
		ratio = exp["ratio"]
		padding = exp["padding"]
		
		if ratio == "auto":
			ratio = bbox.width / float(bbox.height)
			
		if h == "auto":
			h = w / ratio
		elif w == "auto":
			w = h * ratio
	
		return View(bbox, w, h-1, padding=padding)
		
	
	def get_features(self, layer, proj, view):
		"""
		returns a list of projected and filtered features of a layer
		"""
		id = layer['id']
		src = self.layers[id]
		
		if layer['filter'] is False: 
			filter = None
			attr = None
		else:
			attr = layer['filter']['attribute']
			if 'equals' in layer['filter']:
				filter = lambda id: id in layer['filter']['equals']
			elif 'greater-than' in layer['filter']:
				filter = lambda v: v >= layer['filter']['greater-than']
			elif 'less-than' in layer['filter']:
				filter = lambda v: v <= layer['filter']['less-than']
		
		
		features = src.get_features(attr, filter)
		for feature in features:
			feature.project(proj)
			feature.project_view(view)
			
		return features