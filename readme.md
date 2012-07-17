# Kartograph.py

Kartograph is a Python library that generates SVG maps from ESRI shapefiles. Please have a look at the [API docs](https://github.com/kartograph/kartograph.py/wiki/API) for more details.

### Author

Kartograph was created by [Gregor Aisch](http://github.com/gka/). It is supported by [Piwik Web Analytics](http://piwik.org) and the [Open Knowledge Foundation](http://okfn.org). 

### License

Kartograph.py is licensed under [AGPL](http://www.gnu.org/licenses/agpl-3.0.txt)

### Testing the next release

Feel free to test the upcoming release of Kartograph while it is been developed. To do so I strongly recommend to use [virtualenv](http://www.virtualenv.org/en/latest/index.html) and [virtualenv-wrapper](http://www.doughellmann.com/projects/virtualenvwrapper/) in order to avoid conflicts between different versions of Kartograph. To do so, please uninstall your current version, and re-install both in different virtual environments.

````sh
mkdir kpy-new
git clone git@github.com:kartograph/kartograph.py.git -b kartograph-2 kpy-new
# create and activate a new virtual environment
workon kartograph-new
cd kpy-new
python setup.py install
```



