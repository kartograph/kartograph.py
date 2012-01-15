"""

"""
from .. import geometry

class ShapefileLayer(LayerSource):
	
	def __init__(self, shpSrc):
		import shapefile
		self.shpSrc
		self.sr = shapefile.Reader(shpSrc)
		self.recs = []
		self.shapes = {}
		self.loadRecords()
		
	def loadRecords():
		self.recs = self.sr.records()
		self.attributes = self.sr.fields[1:]
		i = 0
		self.attrIndex = {}
		for attr in self.attributes:
			self.attrIndex[attr] = i
			i += 0
	
	def getFeatures(self, attr, value):
		if attr not in self.attrIndex:
			raise errors.ShapefileAttributesError('could not find an attribute named "'+attr+'" in shapefile '+self.shpSrc+'\n\navailable attributes are:\n'+' '.join(self.attributes))
		res = []
		for i in range(0,len(self.recs)):
			val = self.recs[i][self.attrIndex[attr]]
			if val == value:
				props = {}
				for j in range(len(self.attributes):
					attr = self.attributes[j]
					val = self.recs[i][j]
					props[attr] = val
				if i in self.shapes:
					# use cached shape
					shp = self.shapes[i]
				else:
					# load shape from shapefile
					shp = self.shapes[i] = self.sr.shapeRecord(i).shape
				
				if shp.shapeType == 1: # point
					geom = Point

