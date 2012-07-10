
from layersource import LayerSource
from kartograph.errors import *
from kartograph.geometry import create_feature
import shapely.wkb

verbose = False


class OpenStreetMapLayer(LayerSource):
    """
    this class handles shapefile layers
    """

    def __init__(self, src, osm_query='1', osm_type='polygon'):
        """
        initialize shapefile reader
        """
        import psycopg2
        self.conn = psycopg2.connect(src)
        self.type = osm_type
        self.query = osm_query
        self.query_cache = dict()

    def load_feature_meta(self):
        cur = self.conn.cursor()
        # At first we find out what properties are available
        fields = []
        cur.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'planet_osm_%s';" % self.type)
        for rec in cur:
            if rec[0] not in ('way', 'z_order'):
                fields.append(rec[0])

        self.ids = []
        self.metaById = {}
        cur.execute('SELECT "%s" FROM planet_osm_%s WHERE %s' % ('", "'.join(fields), self.type, self.query))
        for rec in cur:
            meta = {}
            for f in range(len(fields)):
                if rec[f]:
                    meta[fields[f]] = rec[f]
            self.ids.append(meta['osm_id'])
            self.metaById[meta['osm_id']] = meta

    def get_features(self, filter=None, bbox=None, verbose=False, ignore_holes=False, min_area=False, charset='utf-8'):
        """
        ### Get features
        """
        # build query
        query = self.query
        if query == '':
            query = 'true'
        if bbox:
            bbox_coords = (bbox[0], bbox[2], bbox[1], bbox[2], bbox[1], bbox[3], bbox[0], bbox[3], bbox[0], bbox[2])
            bbox_poly = 'POLYGON((%f %f, %f %f, %f %f, %f %f, %f %f))' % bbox_coords
            query = "(%s) AND ST_Intersects( way, ST_SetSRID(ST_GeomFromEWKT('%s'), 4326) )" % (query, bbox_poly)

        print "reading from postgis database / " + self.query

        # Open database connection
        cur = self.conn.cursor()
        # Retreive the property names from schema table
        fields = []
        cur.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'planet_osm_%s';" % self.type)
        for rec in cur:
            fields.append(rec[0])

        # Create a store for properties
        features = []
        # Query features
        cur.execute('SELECT "%s" FROM planet_osm_%s WHERE %s' % ('", "'.join(fields), self.type, query))

        for rec in cur:
            # Populate property dictionary
            meta = {}
            geom_wkb = None
            geom = None
            for f in range(len(fields)):
                if fields[f] != 'way':
                    # but ignore null values
                    if rec[f]:
                        if isinstance(rec[f], (str, unicode)):
                            try:
                                meta[fields[f]] = rec[f].decode('utf-8')
                            except:
                                print 'decoding error', fields[f], rec[f]
                                meta[fields[f]] = '--decoding error--'
                        else:
                            meta[fields[f]] = rec[f]
                else:
                    geom_wkb = rec[f]

            if filter is None or filter(meta):
                # construct geometry
                geom = shapely.wkb.loads(geom_wkb.decode('hex'))
                # Finally we construct the map feature and append it to the
                # result list
                features.append(create_feature(geom, meta))

        return features
