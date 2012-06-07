

from kartograph.renderer import MapRenderer
from kartograph.errors import KartographError
from pykml.factory import KML_ElementMaker as KML


class KmlRenderer(MapRenderer):

    def render(self):
        self._init_kml_canvas()
        self._store_layers_kml()

    def write(self, filename):
        outfile = open(filename, 'w')
        from lxml import etree
        outfile.write(etree.tostring(self.kml, pretty_print=True))

    def preview(self):
        self.write('tmp.kml')
        from subprocess import call
        call(["open", "tmp.kml"])

    def _init_kml_canvas(self):
        self.kml = KML.kml(
            KML.Document(
                KML.name('kartograph map')
            )
        )

    def _store_layers_kml(self):
        """
        store features in kml (projected to WGS84 latlon)
        """
        from pykml.factory import KML_ElementMaker as KML

        for layer in self.map.layers:
            if len(layer.features) == 0:
                continue  # ignore empty layers
            g = KML.Folder(
                KML.name(id)
            )
            for feat in layer.features:
                g.append(self._render_feature(feat, layer.options['attributes']))
            self.kml.Document.append(g)

    def _render_feature(self, feature, attributes=[]):
        path = self._render_geometry(feature.geometry)

        pm = KML.Placemark(
            KML.name(unicode(feature.props[attributes[0]['src']])),
            path
        )

        xt = KML.ExtendedData()

        for cfg in attributes:
            if 'src' in cfg:
                if cfg['src'] not in feature.props:
                    continue
                    #raise KartographError(('attribute not found "%s"'%cfg['src']))
                val = feature.props[cfg['src']]
                import unicodedata
                if isinstance(val, str):
                    val = unicode(val, errors='ignore')
                    val = unicodedata.normalize('NFKD', val).encode('ascii', 'ignore')
                xt.append(KML.Data(
                    KML.value(unicode(val)),
                    name=cfg['tgt']
                ))
            elif 'where' in cfg:
                src = cfg['where']
                tgt = cfg['set']
                if len(cfg['equals']) != len(cfg['to']):
                    raise KartographError('attributes: "equals" and "to" arrays must be of same length')
                for i in range(len(cfg['equals'])):
                    if feature.props[src] == cfg['equals'][i]:
                        xt.append(KML.Data(
                            KML.value(cfg['to'][i]),
                            name=tgt
                        ))
        pm.append(xt)

        return pm

    def _render_geometry(self, geometry):
        from shapely.geometry import Polygon, MultiPolygon
        if isinstance(geometry, (Polygon, MultiPolygon)):
            return self._render_polygon(geometry)
        else:
            raise KartographError('kml-renderer is not fully implemented yet')

    def _render_polygon(self, geometry):
        """
        renders a Polygon or MultiPolygon as KML node
        """
        geoms = hasattr(geometry, 'geoms') and geometry.geoms or [geometry]

        kml_polys = []

        for geom in geoms:
            poly = KML.Polygon(
                KML.tesselate("1")
            )
            outer = KML.outerBoundaryIs()
            coords = ''
            for pt in geom.exterior.coords:
                coords += ','.join(map(str, pt)) + ' '
            outer.append(KML.LinearRing(
                KML.coordinates(coords)
            ))
            poly.append(outer)
            inner = KML.innerBoundaryIs()
            for hole in geom.interiors:
                coords = ''
                for pt in hole.coords:
                    coords += ','.join(map(str, pt)) + ' '
                inner.append(KML.LinearRing(
                    KML.coordinates(coords)
                ))
            if len(inner) > 0:
                poly.append(inner)
            kml_polys.append(poly)

        if len(kml_polys) == 1:
            return kml_polys[0]
        multigeometry = KML.MultiGeometry()
        for p in kml_polys:
            multigeometry.append(p)
        return multigeometry
