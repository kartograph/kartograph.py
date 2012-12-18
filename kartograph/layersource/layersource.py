
import os.path
import os
from kartograph.errors import *


class LayerSource:
    """
    base class for layer source data providers (e.g. shapefiles)
    """
    def get_features(self, filter=None, bbox=None, ignore_holes=False, charset='utf-8'):
        raise NotImplementedError()

    def find_source(self, src):
        if not os.path.exists(src) and 'KARTOGRAPH_DATA' in os.environ:
            # try
            paths = os.environ['KARTOGRAPH_DATA'].split(os.pathsep)
            for path in paths:
                if path[:-1] != os.sep and src[0] != os.sep:
                    path = path + os.sep
                if os.path.exists(path + src):
                    src = path + src
                    break
            if not os.path.exists(src):
                raise KartographError('layer source not found: %s' % src)
        return src
