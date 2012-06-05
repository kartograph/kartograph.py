
"""
package geometry.feature
"""

__all__ = ['Feature', 'MultiPolygonFeature', 'create_feature']

from Feature import Feature
from MultiPolygonFeature import MultiPolygonFeature


def create_feature(geom, props):
    """ checks geometry type and returns the appropriate feature type """
    if geom.type in ('Polygon', 'MultiPolygon'):
        return MultiPolygonFeature(geom, props)
    else:
        raise NotImplementedError('create feature not implemented for geometry type ' + geom.type)
