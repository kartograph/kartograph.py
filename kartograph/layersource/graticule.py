
from kartograph.geometry import Line, Feature
from layersource import LayerSource

class GraticuleLayer(LayerSource):
	"""
	special layer source for grid of longitudes and latitudes (graticule)
	"""
	
	def get_features(self, step, proj, bbox=[-180,-90,180,90]):
		"""
		returns a list of line features that make up
		the graticule
		"""
		minLat = max(proj.minLat, bbox[1])
		maxLat = min(proj.maxLat, bbox[3])
		minLon = bbox[0]
		maxLon = bbox[2]
		
		def xfrange(start, stop, step):
			while (step > 0 and start < stop) or (step < 0 and start > step):
				yield start
				start += step
		
		
		line_features = []
		# latitudes
		for lat in xfrange(0,90, step[1]):
			lats = ([lat, -lat], [0])[lat == 0]
			for lat_ in lats:
				if lat_ < minLat or lat_ > maxLat:
					continue
				pts = []
				props = { 'lat': lat_ }
				for lon in xfrange(0,361,0.5):
					lon_ = lon-180
					if lon_ < minLon or lon_ > maxLon:
						continue
					pts.append((lon_, lat_))					
				if len(pts) > 1:
					line = Feature(Line(pts), props)
					line_features.append(line)
		
		# longitudes			
		for lon in xfrange(0,181, step[0]):
			lons = ([lon, -lon], [lon])[lon == 0 or lon == 180]
			for lon_ in lons:
				if lon_ < minLon or lon_ > maxLon:
					continue
				pts = []
				props = { 'lon': lon_ }
				lat_range = xfrange(step[0], 181-step[0],1)
				if lon_ % 90 == 0:
					lat_range = xfrange(0, 181,1)
				for lat in lat_range:
					lat_ = lat-90
					if lat_ < minLat or lat_ > maxLat:
						continue
					pts.append((lon_, lat_))
				if len(pts) > 1:
					line = Feature(Line(pts), props)
					line_features.append(line)
		
		return line_features