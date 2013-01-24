
from kartograph.geometry import MultiLineFeature
from kartograph.layersource.layersource import LayerSource
from shapely.geometry import LineString


class GraticuleLayer(LayerSource):
    """
    special layer source for grid of longitudes and latitudes (graticule)
    """
    def get_features(self, latitudes, longitudes, proj, bbox=[-180, -90, 180, 90]):
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
        for lat in latitudes:
            if lat < minLat or lat > maxLat:
                continue
            pts = []
            props = {'lat': lat}
            for lon in xfrange(-180, 181, 0.5):
                if lon < minLon or lon > maxLon:
                    continue
                #if isinstance(proj, Azimuthal):
                #    lon += proj.lon0
                #    if lon < -180:
                #        lon += 360
                #    if lon > 180:
                #        lon -= 360
                if proj._visible(lon, lat):
                    pts.append((lon, lat))
            if len(pts) > 1:
                line = MultiLineFeature(LineString(pts), props)
                line_features.append(line)
        # print line_features

        # longitudes
        for lon in longitudes:
            if lon < minLon or lon > maxLon:
                continue
            pts = []
            props = {'lon': lon}
            #lat_range = xfrange(step[0], 181-step[0],1)
            #if lon % 90 == 0:
            #    lat_range = xfrange(0, 181,1)
            for lat in xfrange(0, 181, 0.5):
                lat_ = lat - 90
                if lat_ < minLat or lat_ > maxLat:
                    continue
                if proj._visible(lon, lat_):
                    pts.append((lon, lat_))
            if len(pts) > 1:
                line = MultiLineFeature(LineString(pts), props)
                line_features.append(line)

        return line_features
