
# Kartograph and OpenStreetMap

### Setup PostgreSQL and PostGIS

    brew install postgresql
    brew install postgis

### Initialize new PostGIS-enabled database

    createdb osm
    psql -d osm -f /usr/local/Cellar/postgis/1.5.3/share/postgis/postgis.sql
    psql -d osm -f /usr/local/Cellar/postgis/1.5.3/share/postgis/spatial_ref_sys.sql

### Download OpenStreetMap dump

For instance, you can downlaod the OSM dump provided by Cloudmade. The output is unpacked on thy fly.

    wget -O - http://downloads.cloudmade.com/europe/western_europe/germany/germany.osm.bz2 | bzcat > germany.osm

### Import OSM dump into PostGIS

Make sure you have enough time and memory for this operation. On my Macbook it took more than 4 hours to read the dump of Germany.

    osm2pgsql -l -C 2000 -d osm germany.osm