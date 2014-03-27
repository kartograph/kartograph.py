
from layersource import LayerSource
from kartograph.errors import *
from kartograph.geometry import create_feature
import shapely.wkb

verbose = False


class PostGISLayer(LayerSource):
    """
    This class handles PostGIS layers. You need a running PostgreSQL server
    with a PostGIS enabled database that stores your geodata.
    """

    def __init__(self, src, query='true', table='planet_osm_polygon'):
        """
        Initialize database connection
        """
        try:
            import psycopg2
        except ImportError:
            raise KartographError('You need to install psycopg2 (and PostgreSQL) if you want to render maps from PostGIS.\ne.g.\n    pip install psycopg2')
        self.conn = psycopg2.connect(src)
        self.query = query
        self.query_cache = dict()
        self.table = table

        cur = self.conn.cursor()

        # Read list of available properties
        self.fields = []
        cur.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s';" % self.table)
        for rec in cur:
            self.fields.append(rec[0])

        # Find out which column stores the geoemtry data
        cur.execute("SELECT f_geometry_column FROM geometry_columns WHERE f_table_name = '%s'" % self.table)
        self.geom_col = cur.fetchone()[0]

    def get_features(self, filter=None, bbox=None, verbose=False, ignore_holes=False, min_area=False, charset='utf-8'):
        """
        ### Get features
        """
        # build query
        query = self.query
        if query == '':
            query = 'true'
        if bbox:
            # Check for intersection with bounding box
            bbox_coords = (bbox[0], bbox[2], bbox[1], bbox[2], bbox[1], bbox[3], bbox[0], bbox[3], bbox[0], bbox[2])
            bbox_poly = 'POLYGON((%f %f, %f %f, %f %f, %f %f, %f %f))' % bbox_coords
            query = "(%s) AND ST_Intersects( %s, ST_SetSRID(ST_GeomFromEWKT('%s'), 4326) )" % (query, self.geom_col, bbox_poly)

        # print "reading from postgis database / " + self.query

        # Open database connection
        cur = self.conn.cursor()
        fields = self.fields

        # Create a store for properties
        features = []
        # Query features
        cur.execute('SELECT "%s" FROM %s WHERE %s' % ('", "'.join(fields), self.table, query))

        for rec in cur:
            # Populate property dictionary
            meta = {}
            geom_wkb = None
            geom = None
            for f in range(len(fields)):
                if fields[f] != self.geom_col:
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
                    # Store geometry
                    geom_wkb = rec[f]

            if filter is None or filter(meta):
                # construct geometry
                geom = shapely.wkb.loads(geom_wkb.decode('hex'))
                # Finally we construct the map feature and append it to the
                # result list
                features.append(create_feature(geom, meta))

        return features
