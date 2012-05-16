
from kartograph.errors import KartographError
import re


class Feature:
    """
    feature = geometry + properties
    geometry should be shapely geometry
    """
    def __init__(self, geometry, properties):
        self.geometry = geometry
        self.properties = properties

    def __repr__(self):
        return 'Feature(' + self.geometry.__class__.__name__ + ')'

    def project(self, proj):
        self.project_geometry(proj)

    def unify(self, point_store, precision=None):
        from kartograph.simplify import unify_polygons
        contours = self.contours
        contours = unify_polygons(contours, point_store, precision)
        self.apply_contours(contours)

    def project_view(self, view):
        self.geometry = self.geometry.project_view(view)

    def crop_to(self, geometry):
        self.geometry = self.geometry.intersection(geometry)

    def substract_geom(self, geom):
        self.geometry = self.geometry.substract_geom(geom)

    def geometry_to_svg(self, svg, round):
        raise NotImplementedError('geometry_to_svg() needs to be implemented by geometry specific Feature classes')

    def geometry_to_kml(self, svg, round):
        raise NotImplementedError('geometry_to_kml() needs to be implemented by geometry specific Feature classes')

    def project_geometry(self, proj):
        raise NotImplementedError('project_geometry() needs to be implemented by geometry specific Feature classes')

    def to_svg(self, svg, round, attributes=[], styles=None):
        node = self.geometry_to_svg(svg, round)
        if node is None:
            return None
        # todo: add data attribtes
        for cfg in attributes:
            if 'src' in cfg:
                tgt = re.sub('(\W|_)+', '-', cfg['tgt'].lower())
                if cfg['src'] not in self.props:
                    continue
                    #raise KartographError(('attribute not found "%s"'%cfg['src']))
                val = self.props[cfg['src']]
                import unicodedata
                if isinstance(val, str):
                    val = unicode(val, errors='ignore')
                    val = unicodedata.normalize('NFKD', val).encode('ascii', 'ignore')
                if isinstance(val, (int, float)):
                    val = str(val)
                node.setAttribute('data-' + tgt, val)

            elif 'where' in cfg:
                # can be used to replace attributes...
                src = cfg['where']
                tgt = cfg['set']
                if len(cfg['equals']) != len(cfg['to']):
                    raise KartographError('attributes: "equals" and "to" arrays must be of same length')
                for i in range(len(cfg['equals'])):
                    if self.props[src] == cfg['equals'][i]:
                        node.setAttribute('data-' + tgt, cfg['to'][i])

        if '__color__' in self.props:
            node.setAttribute('fill', self.props['__color__'])
        return node

    def to_kml(self, round, attributes=[]):
        path = self.geometry_to_kml(round)
        from pykml.factory import KML_ElementMaker as KML

        pm = KML.Placemark(
            KML.name(self.props[attributes[0]['src']]),
            path
        )

        xt = KML.ExtendedData()

        for cfg in attributes:
            if 'src' in cfg:
                if cfg['src'] not in self.props:
                    continue
                    #raise KartographError(('attribute not found "%s"'%cfg['src']))
                val = self.props[cfg['src']]
                import unicodedata
                if isinstance(val, str):
                    val = unicode(val, errors='ignore')
                    val = unicodedata.normalize('NFKD', val).encode('ascii', 'ignore')
                xt.append(KML.Data(
                    KML.value(val),
                    name=cfg['tgt']
                ))
            elif 'where' in cfg:
                src = cfg['where']
                tgt = cfg['set']
                if len(cfg['equals']) != len(cfg['to']):
                    raise KartographError('attributes: "equals" and "to" arrays must be of same length')
                for i in range(len(cfg['equals'])):
                    if self.props[src] == cfg['equals'][i]:
                        #svg['data-'+tgt] = cfg['to'][i]
                        xt.append(KML.Data(
                            KML.value(cfg['to'][i]),
                            name=tgt
                        ))
        pm.append(xt)

        return pm

    def is_empty(self):
        return self.geom is not None

    @property
    def geom(self):
        return self.geometry

    @property
    def props(self):
        return self.properties
