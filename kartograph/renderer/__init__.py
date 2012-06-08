

class MapRenderer(object):

    def __init__(self, map, src_encoding=None):
        self.map = map
        self.src_encoding = src_encoding

    def render(self):
        pass

    def write(self, filename):
        raise 'Not implemented yet'

    def preview(self):
        raise 'Not implemented yet'


from svg import SvgRenderer
from kml import KmlRenderer

__all__ = ['MapRenderer', 'SvgRenderer', 'KmlRenderer']
