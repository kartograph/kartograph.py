
from point import Point


class BBox(object):
    """ 2D bounding box """
    def __init__(self, width=None, height=None, left=0, top=0):
        import sys
        if width == None:
            self.xmin = sys.maxint
            self.xmax = sys.maxint * -1
        else:
            self.xmin = self.left = left
            self.xmax = self.right = left + width
            self.width = width
        if height == None:
            self.ymin = sys.maxint
            self.ymax = sys.maxint * -1
        else:
            self.ymin = self.top = top
            self.ymax = self.bottom = height + top
            self.height = height

    def update(self, pt):
        if not isinstance(pt, Point):
            pt = Point(pt[0], pt[1])
        self.xmin = min(self.xmin, pt.x)
        self.ymin = min(self.ymin, pt.y)
        self.xmax = max(self.xmax, pt.x)
        self.ymax = max(self.ymax, pt.y)

        self.left = self.xmin
        self.top = self.ymin
        self.right = self.xmax
        self.bottom = self.ymax
        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin

    def intersects(self, bbox):
        """ returns true if two bounding boxes overlap """
        return bbox.left < self.right and bbox.right > self.left and bbox.top < self.bottom and bbox.bottom > self.top

    def check_point(self, pt):
        """ check if a point is inside the bbox """
        return pt[0] > self.xmin and pt[0] < self.xmax and pt[1] > self.ymin and pt[1] < self.ymax

    def __str__(self):
        return '[%.2f, %.2f, %.2f, %.2f]' % (self.left, self.top, self.width, self.height)

    def join(self, bbox):
        self.update(Point(bbox.left, bbox.top))
        self.update(Point(bbox.right, bbox.bottom))

    def inflate(self, amount):
        self.xmin -= amount
        self.ymin -= amount
        self.xmax += amount
        self.ymax += amount

        self.left = self.xmin
        self.top = self.ymin
        self.right = self.xmax
        self.bottom = self.ymax
        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin
