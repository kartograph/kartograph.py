# Installing Kartograph on Windows

## Installing PostgreSQL and PostGIS

Install PostgreSQL using the [one-click installer](http://www.enterprisedb.com/products-services-training/pgdownload) (e.g. ``postgresql-9.1.4-1-windows.exe``). During install you will be asked for a master password, which you need to keep for later. 

* At the end of the install you will be asked to install the Stack Builder. Say yes, and install *Spatial Extensions/PostGIS 2.0 for PostgreSQL 9.1 v 2.0.0*.
* Instead of using the Stack Builder you can also install PostGIS seperately using the [one-click installer](http://postgis.refractions.net/download/windows/). Make sure you pick the right build for your PostgreSQL version (e.g. ``postgis-pg91-setup-2.0.1-1.exe``).

Installing PostGIS will also install the required GDAL framework. In case you absolutely don't want to install PostGIS and PostgreSQL you need to install [GDAL](http://pypi.python.org/pypi/GDAL/1.9.1#windows) on your own.

## Install shapely

