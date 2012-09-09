

class Point():
    """ base class for points, used by line and bbox """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def project(self, proj):
        (x, y) = proj.project(self.x, self.y)
        self.x = x
        self.y = y

    """emulate python's container types"""
    def __len__(self):
        return 2

    def __getitem__(self, k):
        pt = (self.x, self.y)
        return pt[k]

    def __setitem__(self, k, value):
        if k == 0:
            self.x = value
        elif k == 1:
            self.y = value
        else:
            raise IndexError

    def __delitem__(self, key):
        raise TypeError('deletion not supported')
