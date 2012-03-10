# Step by Step Installation Instructions

Tested on Mac OS 10.6.8


## Automatic Install

1. Download kartograph.py

```bash
git clone https://github.com/kartograph/kartograph.py kartograph
```

2. Use setup.py to install Kartograph + required libraries

```bash
cd kartograph
sudo python setup.py intstall
```

## Test installation

Kartograph at least needs a shapefile to create a svg map from. You can download public domain shapefiles from [naturalearthdata.com](http://www.naturalearthdata.com/downloads/). If you only want to test the installation, grab and unzip the following shapefile of the United States.

```bash
wget http://data.kartograph.org/united-states.zip
unzip united-states.zip -d shp
```

Now create a very simple map configuration and store it to ``map.yaml``

```yaml
layers:
-  src: shp/united-states.shp
bounds:
   mode: bbox
   data: [-120,25,-73,50]
```

Now you can generate the SVG map using

```bash
kartograph svg map.yaml -o states.svg
```

If you want to preview generated maps automatically, save the following script to ```/usr/local/bin/firefox` (make sure to point it to the location where you installed Firefox on your system).

```bash
#!/bin/sh
open -a /Applications/Firefox.app $1
```



## Manual Install

You need to install required libraries

###shapefile (http://code.google.com/p/pyshp/)

One of the following should work

	sudo pypm install pyshp
	easy_install pyshp


### Polygon

This should work:

	pip install polygon

Alternatively download mac binaries from 

http://pypi.python.jp/Polygon/Polygon-2.0.4.macosx-10.6-universal.tar.gz#md5=302abdd94b25ccd5e3a7cbbd7635d777

and copy the folder "Polygon" into

/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/

### SvgFig

Follow instructions here:

http://code.google.com/p/svgfig/wiki/HowToInstall

## Download kartograph.py

	git clone https://github.com/kartograph/kartograph.py

Output should look like this:

	Cloning into kartograph.py...
	remote: Counting objects: 422, done.
	remote: Compressing objects: 100% (265/265), done.
	remote: Total 422 (delta 210), reused 353 (delta 141)
	Receiving objects: 100% (422/422), 38.82 MiB | 458 KiB/s, 	Resolving deltas: 100% (210/210), done.

