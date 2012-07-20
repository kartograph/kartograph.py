
"""
package geometry.feature
"""

__all__ = ['Feature', 'MultiPolygonFeature', 'create_feature', 'MultiLineFeature', 'PointFeature']

from Feature import Feature
from MultiPolygonFeature import MultiPolygonFeature
from MultiLineFeature import MultiLineFeature
from PointFeature import PointFeature


def create_feature(geom, props):
    """ checks geometry type and returns the appropriate feature type """
    if geom.type in ('Polygon', 'MultiPolygon'):
        return MultiPolygonFeature(geom, props)
    elif geom.type in ('LineString', 'MultiLineString'):
        return MultiLineFeature(geom, props)
    elif geom.type in ('Point'):
        return PointFeature(geom, props)
    else:
        raise NotImplementedError('create feature not implemented for geometry type ' + geom.type)
