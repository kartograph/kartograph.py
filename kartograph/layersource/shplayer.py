
from layersource import LayerSource


class ShapefileLayer(LayerSource):
	"""
	this class handles shapefile layers
	"""
	
	def __init__(self, src):
		"""
		initialize shapefile reader
		"""
		import shapefile
		if isinstance(src, unicode):
			src = src.encode('ascii', 'ignore')			
		self.shpSrc = src
		self.sr = shapefile.Reader(src)
		self.recs = []
		self.shapes = {}
		self.loadRecords()
	
	
	def loadRecords(self):
		"""
		load shapefile records into memory. note that only the records are loaded and not the shapes.
		"""
		self.recs = self.sr.records()
		self.attributes = []
		for a in self.sr.fields[1:]:
			self.attributes.append(a[0])
		i = 0
		self.attrIndex = {}
		for attr in self.attributes:
			self.attrIndex[attr] = i
			i += 0
			
	
	def getShape(self, i):
		"""
		returns a shape of this shapefile. if requested for the first time, the shape is loaded from shapefile (slow)
		"""
		if i in self.shapes: # check cache
			shp = self.shapes[i]
		else: # load shape from shapefile
			shp = self.shapes[i] = self.sr.shapeRecord(i).shape
		return shp
		
	
	def getFeatures(self, attr, value):
		"""
		returns a list of features matching to the attr -> value pair
		"""
		if attr not in self.attrIndex:
			raise errors.ShapefileAttributesError('could not find an attribute named "'+attr+'" in shapefile '+self.shpSrc+'\n\navailable attributes are:\n'+' '.join(self.attributes))
		res = []
		for i in range(0,len(self.recs)):
			val = self.recs[i][self.attrIndex[attr]]
			if val == value:
				props = {}
				for j in range(len(self.attributes)):
					attr = self.attributes[j]
					val = self.recs[i][j]
					props[attr] = val
					
				shp = self.getShape(i)
				
				if shp.shapeType == 5: # multi-polygon
					geom = points2polygon(shp)
		

def points2polygon(shp):
	parts = shp.parts[:]
	parts.append(len(shp.points))
	polys = []
	
	for j in range(len(parts)-1):
		pts = shp.points[parts[j]:parts[j+1]]
		if j == 0:
	
		lats = []
		lons = []
		for k in range(0,len(pts)):
			lats.append(pts[k][1])
			lons.append(pts[k][0])
	
		poly_points = []
		x, y = proj(lons, lats)
		for i in range(len(x)):
			pt = view.project(Point(x[i], y[i]))
			pt.y = view.height - pt.y
			poly_points.append(pt)
		polygon = Polygon(id, poly_points, mode='point')
		if polygon != None:                                                                                                                                   
			polys.append(polygon)                                                                                                                              
	return polys
