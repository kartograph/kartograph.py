## Kartograph is not maintained anymore

As you probably already guessed from the commit history in this repo, Kartograph.py is **not maintained**, which means that bugs are not being fixed and new features are not being added anymore. The original maintainer decided to move on with his life. 

Bummer, I know! But... there is a great alternative!

I highly recommend using [mapshaper](https://github.com/mbloch/mapshaper) instead, either the web gui or via command-line. It's what I use for all my mapping needs nowadays.

Of course, if anyone wants to take over, kartograph.py is all yours.

---------

# Kartograph.py

Kartograph is a Python library that generates SVG maps from ESRI shapefiles. Please have a look at the [API docs](https://github.com/kartograph/kartograph.py/wiki/API) for more details.

### Author

Kartograph was created by [Gregor Aisch](http://github.com/gka/) and is supported by [dpa-newslab](http://www.dpa-newslab.com/), [Piwik Web Analytics](http://piwik.org) and the [Open Knowledge Foundation](http://okfn.org). 

### License

Kartograph.py is licensed under [AGPL](http://www.gnu.org/licenses/agpl-3.0.txt)

### Current status

Kartograph.py is still beta, which means that there are some bugs left to fix.

However, feel free to test it while it is been developed. To do so I recommend to use [virtualenv](http://www.virtualenv.org/en/latest/index.html) and [virtualenv-wrapper](http://www.doughellmann.com/projects/virtualenvwrapper/).

```sh
> mkdir kartograph-py
> git clone git@github.com:kartograph/kartograph.py.git kartograph-py

# create and activate a new virtual environment
> mkvirtualenv kartograph

# install and use Kartograph
(kartograph)> cd kartograph-py
(kartograph)> python setup.py install
```

See install documentation
