
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
		print bbox, bbox.width/bbox.height
		
		view = self.get_view(opts, bbox)
		view_poly = bounds_poly.project_view(view)
		
		svg = self.init_svg_canvas(opts, proj, view, bbox)
		
		layers = []
		layerOpts = {}
		layerFeatures = {}

		# get features
		for layer in opts['layers']:
			id = layer['id']
			layerOpts[id] = layer
			layers.append(id)
			features = self.get_features(layer, proj, view, opts, view_poly)	
			layerFeatures[id] = features
			
		self.simplify_layers(layers, layerFeatures, layerOpts)
		self.crop_layers_to_view(layers, layerFeatures, view_poly)
		self.crop_layers(layers, layerOpts, layerFeatures)
		self.join_layers(layers, layerOpts, layerFeatures)
		self.substract_layers(layers, layerOpts, layerFeatures)
		self.store_layers(layers, layerOpts, layerFeatures, svg, opts)	
		
		if outfile is None:
			svg.firefox()
		else:
			svg.save(outfile)
	
	def prepare_layers(self, opts):
		"""
		prepares layer sources
		"""
		self.layers = layers = {}
		for layer in opts['layers']:
			id = layer['id']
			src = handle_layer_source(layer)
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
			sea = proj.sea_shape()
			return MultiPolygon(sea)
		
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
				
		print bbox		
				
		bbox.inflate(bbox.width * bnds['padding'])
		
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
		
		if ratio == "auto":
			ratio = bbox.width / float(bbox.height)
			
		if h == "auto":
			h = w / ratio
		elif w == "auto":
			w = h * ratio
	
		return View(bbox, w, h-1)
		
	
	def get_features(self, layer, proj, view, opts, view_poly):
		"""
		returns a list of projected and filtered features of a layer
		"""
		id = layer['id']
		src = self.layers[id]
		
		if 'src' in layer: # regular geodata layer
			if layer['filter'] is False: 
				filter = None
				attr = None
			else:
				attr = layer['filter']['attribute']
				incl = layer['filter']['type'] == 'include'
				if incl and 'equals' in layer['filter']:
					filter = lambda id: id in layer['filter']['equals']
				elif not incl and 'equals' in layer['filter']:
					filter = lambda id: id not in layer['filter']['equals']
				elif incl and 'greater-than' in layer['filter']:
					filter = lambda v: v > layer['filter']['greater-than']
				elif not incl and 'greater-than' in layer['filter']:
					filter = lambda v: v <= layer['filter']['greater-than']
				elif incl and 'less-than' in layer['filter']:
					filter = lambda v: v < layer['filter']['less-than']
				elif not incl and 'less-than' in layer['filter']:
					filter = lambda v: v >= layer['filter']['less-than']
			features = src.get_features(attr, filter)
		
		elif 'special' in layer: # special layers need special treatment
			if layer['special'] == "graticule":
				bbox = [-180,-90,180,90]
				if opts['bounds']['mode'] == "bbox":
					bbox = opts['bounds']['data']
				step = layer['step']
				features = src.get_features(step, proj, bbox)
			elif layer['special'] == "sea":
				features = src.get_features(view_poly)
				
		
		for feature in features:
			feature.project(proj)
			feature.project_view(view)
			
		return features
	
	
	def init_svg_canvas(self, opts, proj, view, bbox):
		"""
		prepare a blank new svg file
		"""
		from svgfig import canvas, SVG
		
		w = view.width
		h = view.height+2
		
		svg = canvas(width='%dpx' % w, height='%dpx' % h, viewBox='0 0 %d %d' % (w, h), enable_background='new 0 0 %d %d' % (w, h), style='stroke-width:0.7pt; stroke-linejoin: round; stroke:#000; fill:#f3f3f0;')
	
		css = 'path { fill-rule: evenodd; }\n#context path { fill: #eee; stroke: #bbb; } '
		
		#if options.graticule:
		#	css += '#graticule path { fill: none; stroke-width:0.25pt;  } #graticule .equator { stroke-width: 0.5pt } '
	
		svg.append(SVG('defs', SVG('style', css, type='text/css')))
	
		meta = SVG('metadata')
		views = SVG('views')
		view = SVG('view', padding=str(opts['bounds']['padding']), w=w, h=h)
		proj_ = proj.toXML()
		bbox = SVG('bbox', x=round(bbox.left,2), y=round(bbox.top,2), w=round(bbox.width,2), h=round(bbox.height,2))
		
		ll = [-180,-90,180,90]
		if opts['bounds']['mode'] == "bbox":
			ll = opts['bounds']['data']
		llbbox = SVG('llbbox', lon0=ll[0],lon1=ll[2],lat0=ll[1],lat1=ll[3])
		
		views.append(view)
		view.append(proj_)
		view.append(bbox)
		view.append(llbbox)
		
		meta.append(views)
		svg.append(meta)
		
		return svg
	
	
	def simplify_layers(self, layers, layerFeatures, layerOpts):
		"""
		performs polygon simplification
		"""
		# step 1: unify
		from simplify import create_point_store, simplify_distance
		
		point_store = create_point_store()
		for id in layers:
			for feature in layerFeatures[id]:
				feature.geom.unify(point_store)
				
		print 'unified points:', point_store['removed'], (100*point_store['removed']/(point_store['removed']+point_store['kept'])),'%'
		
		to_simplify = []
		for id in layers:
			if layerOpts[id]['simplify'] is not False:
				to_simplify.append(id)
				
		to_simplify.sort(key=lambda id: layerOpts[id]['simplify'])
		
		for id in to_simplify:
			print 'simplifying',id
			for feature in layerFeatures[id]:
				for pts in feature.geom.points():
					simplify_distance(pts, layerOpts[id]['simplify'])
				feature.geom.update()
		
	
	def crop_layers_to_view(self, layers, layerFeatures, view_poly):
		"""
		cuts the layer features to the map view
		"""
		for id in layers:
			out = []
			for feat in layerFeatures[id]:
				feat.crop_to(view_poly)
				if not feat.is_empty():
					out.append(feat)
			layerFeatures[id] = out


	def crop_layers(self, layers, layerOpts, layerFeatures):
		"""
		handles crop-to
		"""
		for id in layers:
			if layerOpts[id]['crop-to'] is not False:
				cropped_features = []
				for tocrop in layerFeatures[id]:
					cbbox = tocrop.geom.bbox()
					crop_at_layer = layerOpts[id]['crop-to']
					if crop_at_layer not in layers:
						raise KartographError('you want to substract from layer "%s" which cannot be found'%crop_at_layer)
					for crop_at in layerFeatures[crop_at_layer]:
						if crop_at.geom.bbox().intersects(cbbox):
							tocrop.crop_to(crop_at.geom)
							cropped_features.append(tocrop)
				layerFeatures[id] = cropped_features					
			
		
	def substract_layers(self, layers, layerOpts, layerFeatures):
		"""
		handles substract-from 
		"""
		for id in layers:
			if layerOpts[id]['substract-from'] is not False:
				for feat in layerFeatures[id]:
					cbbox = feat.geom.bbox()
					for subid in layerOpts[id]['substract-from']:
						if subid not in layers:
							raise KartographError('you want to substract from layer "%s" which cannot be found'%subid)
						for sfeat in layerFeatures[subid]:
							if sfeat.geom.bbox().intersects(cbbox):
								sfeat.substract_geom(feat.geom)
				layerFeatures[id] = []
				
	
	def join_layers(self, layers, layerOpts, layerFeatures):
		"""
		joins features in layers 
		"""
		from geometry.utils import join_features
		
		for id in layers:
			if layerOpts[id]['join'] is not False:
				join = layerOpts[id]['join']
				groupBy = join['group-by']
				groups = join['groups']
				groupAs = join['group-as']
				groupFeatures = {}
				res = []
				for feat in layerFeatures[id]:
					found_in_group = False
					for g_id in groups:
						if g_id not in groupFeatures:
							groupFeatures[g_id] = []
						if feat.props[groupBy] in groups[g_id]:
							groupFeatures[g_id].append(feat)
							found_in_group = True
							break
					if not found_in_group: res.append(feat)
				for g_id in groups:
					props = {}
					if groupAs is not False:
						props[groupAs] = g_id
					res += join_features(groupFeatures[g_id], props)
				layerFeatures[id] = res
		
	
	def store_layers(self, layers, layerOpts, layerFeatures, svg, opts):
		"""
		store features in svg
		"""
		from svgfig import SVG
		
		for id in layers:
			print id
			if len(layerFeatures[id]) == 0: continue # ignore empty layers
			g = SVG('g', id=id)
			for feat in layerFeatures[id]:
				g.append(feat.to_svg(opts['export']['round'], layerOpts[id]['attributes']))			
			svg.append(g)
							
		