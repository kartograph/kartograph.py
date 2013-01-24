
from layersource import LayerSource
from kartograph.errors import *
from kartograph.geometry import BBox, create_feature
from shapely.geometry import LineString, Point, Polygon

import csv
import pyproj


verbose = False


class CsvLayer(LayerSource):
    """
    this class handles csv layers
    """

    def __init__(self, src, mode, xfield, yfield, dialect, crs):
        """
        initialize shapefile reader
        """
        if isinstance(src, unicode):
            src = src.encode('ascii', 'ignore')
        self.cr = UnicodeReader(open(src), dialect=dialect)
        # read csv header
        self.header = h = self.cr.next()
        # initialize CRS
        self.proj = None
        self.mode = mode
        if crs is not None:
            if isinstance(crs, (str, unicode)):
                self.proj = pyproj.Proj(str(crs))
            elif isinstance(crs, dict):
                self.proj = pyproj.Proj(**crs)

        if xfield not in h or yfield not in h:
            raise KartographError('could not find csv column for coordinates (was looking for "%s" and "%s")' % (xfield, yfield))
        else:
            self.xfield = xfield
            self.yfield = yfield

    def get_features(self, filter=None, bbox=None, ignore_holes=False, charset='utf-8', min_area=0):
        # Eventually we convert the bbox list into a proper BBox instance
        if bbox is not None and not isinstance(bbox, BBox):
            bbox = BBox(bbox[2] - bbox[0], bbox[3] - bbox[1], bbox[0], bbox[1])
        mode = self.mode
        if mode in ('line', 'polygon'):
            coords = []
        features = []
        for row in self.cr:
            attrs = dict()
            for i in range(len(row)):
                key = self.header[i]
                if key == self.xfield:
                    x = float(row[i])
                elif key == self.yfield:
                    y = float(row[i])
                else:
                    attrs[key] = row[i]
            if self.proj is not None:
                # inverse project coord
                x, y = self.proj(x, y, inverse=True)
            if mode == 'points':
                features.append(create_feature(Point(x, y), attrs))
            else:
                coords.append((x, y))
        if mode == 'line':
            features.append(create_feature(LineString(coords), dict()))
        elif mode == 'polygon':
            features.append(create_feature(Polygon(coords), dict()))
        return features


import codecs


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self