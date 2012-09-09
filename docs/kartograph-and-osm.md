
# Kartograph and OpenStreetMap

### Setup PostgreSQL and PostGIS

    brew install postgresql
    brew install postgis
    brew install osm2pgsql

### Initialize a data directory for your and run PostgreSQL

    pg_ctl init -D ./pgdata
    export PGDATA=./pgdata
    pg_ctl start

### Initialize a new PostGIS-enabled database

    createdb osm
    psql -d osm -f /usr/local/Cellar/postgis/1.5.3/share/postgis/postgis.sql
    psql -d osm -f /usr/local/Cellar/postgis/1.5.3/share/postgis/spatial_ref_sys.sql

### Download OpenStreetMap dump

For instance, you can downlaod the OSM dump provided by Cloudmade. The output is unpacked on thy fly.

    wget -O - http://downloads.cloudmade.com/europe/western_europe/germany/germany.osm.bz2 | bzcat > germany.osm

### Import OSM dump into PostGIS using osm2pgsql

Make sure you have enough time and memory for this operation. On my Macbook it took more than 4 hours to read the dump of Germany.

    osm2pgsql -l -C 2000 -d osm germany.osm

### Set up and run a virtual environment for Kartograph

    pip install virtualenv
    virtualenv ENV
    source ENV/bin/activate

### Install Kartograph

    cd kartograph-dpa
    python setup.py develop
