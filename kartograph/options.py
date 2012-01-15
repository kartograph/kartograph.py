
"""
API 2.0
helper methods for validating options dictionary
"""

import os.path, proj, errors


Error = errors.OptionParseError

def is_str(s):
	return isinstance(s, (str, unicode))

def parse_options(opts):
	"""
	check out that the option dict is filled correctly
	"""
	# projection
	parse_proj(opts)
	parse_layers(opts)
	parse_bounds(opts)
	parse_export(opts)


def parse_proj(opts):
	"""
	checks projections
	"""
	if 'proj' not in opts: opts['proj'] = {}
	prj = opts['proj']
	if 'id' not in prj: prj['id'] = 'laea'
	if prj['id'] not in proj.projections:
		raise Error('unknown projection')
	prjClass = proj.projections[prj['id']]
	for attr in prjClass.attributes():
		if attr not in prj:
			prj[attr] = "auto"
	

def parse_layers(opts):
	if 'layers' not in opts: opts['layers'] = []
	l_id = 0
	for layer in opts['layers']:
		if 'src' not in layer:
			raise Error('you need to define the source for your layers')
		if not os.path.exists(layer['src']):
			raise Error('layer source not found: '+layer['src'])
		if 'id' not in layer:
			layer['id'] = 'layer_'+str(l_id)
			l_id += 1
		parse_layer_attributes(layer)
		parse_layer_filter(layer)
		parse_layer_join(layer)
		parse_layer_simplify(layer)	

			
def parse_layer_attributes(layer):
	if 'attributes' not in layer:
		layer['attributes'] = []
		return
	attrs = []
	for attr in layer['attributes']:
		if is_str(attr):
			attrs.append({'src':attr, 'tgt': attr })
		else:
			attrs.append(attr)


def parse_layer_filter(layer):
	if 'filter' not in layer:
		layer['filter'] = False
		return
	filter = layer['filter']
	if 'type' not in filter: filter['type'] = 'include'
	if 'attribute' not in filter: 
		raise Error('layer filter must define an attribute to filter on')
	if 'equals' in filter:
		if is_str(filter['equals']): 
			filter['equals'] = [filter['equals']]
	elif 'greater-than' in filter:
		try:
			filter['greater-than'] = float(filter['greater-than'])
		except ValueError:
			raise Error('could not convert filter value "greater-than" to float')
	elif 'less-than' in filter:
		try:
			filter['less-than'] = float(filter['less-than'])
		except ValueError:
			raise Error('could not convert filter value "less-than" to float')
	else:
		raise Error('you must define either "equals", "greater-than" or "less-than" in the filter')

	
def parse_layer_join(layer):
	if 'join' not in layer:
		layer['join'] = False
		return
		
		
def parse_layer_simplify(layer):
	if 'simplify' not in layer:
		layer['simplify'] = False
		return
	try:
		layer['simplify'] = float(layer['simplify'])
	except ValueError:
		raise Error('could not convert simplification amount to float')

		
def parse_bounds(opts):
	if 'bounds' not in opts: 
		opts['bounds'] = { }
	bounds = opts['bounds']
	if 'mode' not in bounds:
		bounds['mode'] = 'bbox'
	if 'data' not in bounds:
		bounds['data'] = [-180,-90,180,90]
		bounds['mode'] = 'bbox'
	mode = bounds['mode']
	data = bounds['data']
	if mode == "bbox":
		try:
			if len(data) == 4:
				for i in range(0,4):
					data[i] = float(data[i])
			else:
				raise Error('bounds mode bbox requires array with exactly 4 values [lon0,lat0,lon1,lat]')
		except Error as err:
			raise err
		except:
			raise Error('bounds mode bbox requires array with exactly 4 values [lon0,lat0,lon1,lat]') 
	elif mode == "points":
		try:
			for i in range(0,len(data)):
				pt = data[i]
				if len(pt) == 2:
					pt = map(float, pt)
				else:
					raise Error('bounds mode points requires array with (lon,lat) tuples')
		except Error as err:
			raise err
		except:
			raise Error('bounds mode points requires array with (lon,lat) tuples')
	elif mode in ("polygons","polygon"):
		if "layer" not in data or not is_str(data["layer"]):
			raise Error('you must specify a layer for bounds mode '+mode)
		if "attribute" not in data or not is_str(data["attribute"]):
			raise Error('you must specify an attribute for bounds mode '+mode)
		if "ids" not in data:
			raise Error('you must specify a list of ids for bounds mode '+mode)
		if is_str(data["ids"]):
			data["ids"] = [data["ids"]]
		if "min_area" in data:
			try:
				data["min_area"] = float(data["min_area"])
			except:
				raise Error('min_area must be an integer or float')
				

def parse_export(opts):
	if "export" not in opts:
		opts["export"] = {}
	exp = opts["export"]
	if "width" not in exp and "height" not in exp:
		exp["width"] = 1000
		exp["height"] = "auto"
	elif "height" not in exp:
		exp["height"] = "auto"
	elif "width" not in exp:
		exp["width"] = "auto"
		
	if "ratio" not in exp:
		exp["ratio"] = "auto"		