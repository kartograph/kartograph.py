
"""
computes a circle cartogram for a given svg map + data file
"""
import sys

class Cartogram:

    def generate(self, svg_src, attr, csv_src, key, value):
        regions = self.load_regions_from_svg(svg_src, attr)
        data = self.load_csv(csv_src, key, value)
        circles = []
        for id in regions:
            cx, cy = regions[id]
            val = data[id]
            circles.append(Circle(cx, cy, id, val))

        self.attr = attr
        self.key = value
        self.circles = circles
        self.compute_radii()
        self.layout(700)
        self.rescale()
        self.correct()
        self.layout(200, True)
        self.rescale()
        self.correct()
        self.layout(100, False)
        self.rescale()
        self.correct()
        self.to_svg()

    def load_regions_from_svg(self, url, attr):
        import svg as svgdoc
        svg = svgdoc.Document.load(url)
        self.svg = svg
        g = svg.doc.getElementsByTagName('g')[0]
        coords = {}
        for path in g.getElementsByTagName('path'):
            path_str = path.getAttribte('d')
            id = path.getAttribte('data-' + attr)
            poly = restore_poly_from_path_str(path_str)
            coords[id] = poly.center()
        return coords

    def load_csv(self, url, key='id', value='val'):
        import csv
        doc = csv.reader(open(url), dialect='excel-tab')
        head = None
        data = {}
        for row in doc:
            if not head:
                head = row
                sys.stderr.write(head)
            else:
                id = row[head.index(key)].strip()
                val = float(row[head.index(value)])
                data[id] = val
        return data

    def compute_radii(self):
        import sys, math
        minv = 0
        maxv = sys.maxint * -1
        for c in self.circles:
            minv = min(minv, c.value)
            maxv = max(maxv, c.value)

        for c in self.circles:
            c.r = math.pow((c.value - minv) / (maxv - minv), 0.50) * 60
            c.weight = c.value / maxv

    def layout(self, steps=100, correct=False):
        for i in range(steps):
            #if i % 100 == 0:
            #    self.toSVG()
            self.layout_step(correct)

    def layout_step(self, correct=False):
        import math
        pad = 0

        if correct:
            for C in self.circles:
                v = Vector(C.ox - C.x, C.oy - C.y)
                v.normalize()
                v.resize(0.5)
                C._move(v.x, v.y)

        for A in self.circles:
            for B in self.circles:
                if A != B:
                    radsq = (A.r + B.r) * (A.r + B.r)
                    d = A.sqdist(B)
                    if radsq + pad > d:
                        # move circles away from each other
                        v = Vector(B.x - A.x, B.y - A.y)
                        v.normalize()
                        m = (math.sqrt(radsq) - math.sqrt(d)) * 0.25
                        v.resize(m)
                        A._move(v.x * -1 * B.weight, v.y * -1 * B.weight)
                        B._move(v.x * A.weight, v.y * A.weight)

        for C in self.circles:
            C.move()

    def rescale(self):
        from geometry import BBox, View
        svg = self.svg
        svg_view = svg[1][0][0]
        vh = float(svg_view['h'])
        vw = float(svg_view['w'])

        bbox = BBox()
        for c in self.circles:
            r = c.r
            bbox.update((c.x + r, c.y + r))
            bbox.update((c.x + r, c.y - r))
            bbox.update((c.x - r, c.y + r))
            bbox.update((c.x - r, c.y - r))

        view = View(bbox, vw, vh)
        for c in self.circles:
            c.r *= view.scale
            x, y = view.project((c.x, c.y))
            c.x = x
            c.y = y

    def correct(self):
        for A in self.circles:
            intersects = False
            for B in self.circles:
                if A != B:
                    radsq = (A.r + B.r) * (A.r + B.r)
                    d = A.sqdist_o(B)
                    if radsq > d:
                        intersects = True
                        break
            if not intersects:
                A.x = A.ox
                A.y = A.oy

    def to_svg(self):
        svg = self.svg

        g = svg.node('g', svg.root, id="cartogram", fill="red", fill_opacity="0.5")

        for circle in self.circles:
            c = svg.node('circle', g, cx=circle.x, cy=circle.y, r=circle.r)
            c.setAttribute('data-' + self.attr, circle.id)
            c.setAttribute('data-' + self.key.lower(), circle.value)
            g.append(c)

        svg.preview()
        #svg.save('cartogram.svg')


class Circle:

    def __init__(self, x, y, id, value):
        self.x = self.ox = float(x)
        self.y = self.oy = float(y)
        self.id = id
        self.value = float(value)
        self.dx = 0
        self.dy = 0

    def _move(self, x, y):
        self.dx += x
        self.dy += y

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.dx = 0
        self.dy = 0

    def __repr__(self):
        return '<Circle x=%.1f, y=%.1f, id=%s, val=%f >' % (self.x, self.y, self.id, self.value)

    def sqdist(self, circ):
        dx = self.x - circ.x
        dy = self.y - circ.y
        return dx * dx + dy * dy

    def sqdist_o(self, circ):
        dx = self.ox - circ.x
        dy = self.oy - circ.y
        return dx * dx + dy * dy


"""
been too lazy to code this myself, instead I took code from here
http://www.kokkugia.com/wiki/index.php5?title=Python_vector_class
"""


class Vector:
    # Class properties
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    # represent as a string
    def __repr__(self):
        return 'Vector(%s, %s)' % (self.x, self.y)

    '''
       Class Methods / Behaviours
    '''

    def zero(self):
        self.x = 0.0
        self.y = 0.0
        return self

    def clone(self):
        return Vector(self.x, self.y)

    def normalize(self):
        from math import sqrt
        if self.x == 0 and self.y == 0:
            return self
        norm = float(1.0 / sqrt(self.x * self.x + self.y * self.y))
        self.x *= norm
        self.y *= norm
        # self.z *= norm
        return self

    def invert(self):
        self.x = -(self.x)
        self.y = -(self.y)
        return self

    def resize(self, sizeFactor):
        self.normalize
        self.scale(sizeFactor)
        return self

    def minus(self, t):
        self.x -= t.x
        self.y -= t.y
        # self.z -= t.z
        return self

    def plus(self, t):
        self.x += t.x
        self.y += t.y
        # self.z += t.z
        return self

    def roundToInt(self):
        self.x = int(self.x)
        self.y = int(self.y)
        return self

    # Returns the squared length of this vector.
    def lengthSquared(self):
        return float((self.x * self.x) + (self.y * self.y))

    # Returns the length of this vector.
    def length(self):
        from math import sqrt
        return float(sqrt(self.x * self.x + self.y * self.y))

    # Computes the dot product of this vector and vector v2
    def dot(self, v2):
        return (self.x * v2.x + self.y * v2.y)

    # Linearly interpolates between vectors v1 and v2 and returns the result point = (1-alpha)*v1 + alpha*v2.
    def interpolate(self, v2, alpha):
        self.x = float((1 - alpha) * self.x + alpha * v2.x)
        self.y = float((1 - alpha) * self.y + alpha * v2.y)
        return Vector(self.x, self.y)

    # Returns the angle in radians between this vector and the vector parameter;
    # the return value is constrained to the range [0,PI].
    def angle(self, v2):
        from math import acos
        vDot = self.dot(v2) / (self.length() * v2.length())
        if vDot < -1.0:
            vDot = -1.0
        if vDot > 1.0:
            vDot = 1.0
        return float(acos(vDot))

    # Limits this vector to a given size.
    # NODEBOX USERS: name should change as 'size' and 'scale' are reserved words in Nodebox!
    def limit(self, size):
        if (self.length() > size):
            self.normalize()
            self.scale(size)

    # Point Methods
    # Returns the square of the distance between this tuple and tuple t1.
    def distanceSquared(self, t1):
        dx = self.x - t1.x
        dy = self.y - t1.y
        return (dx * dx + dy * dy)

    # NODEBOX USERS: name should change as 'scale' is reserved word in Nodebox!
    def scale(self, s):
        self.x *= s
        self.y *= s
        return self

    # NODEBOX USERS: name should change as 'translate' is reserved word in Nodebox!
    def translate(self, vec):
        self.plus(vec)

    def distance(self, pt):
        from math import sqrt
        dx = self.x - pt.x
        dy = self.y - pt.y
        return float(sqrt(dx * dx + dy * dy))


def restore_poly_from_path_str(path_str):
    """
    restores a list of polygons from a SVG path string
    """
    contours = path_str.split('Z')  # last contour may be empty
    from Polygon import Polygon as Poly
    poly = Poly()
    for c_str in contours:
        if c_str.strip() != "":
            pts_str = c_str.strip()[1:].split("L")
            pts = []
            for pt_str in pts_str:
                x, y = map(float, pt_str.split(','))
                pts.append((x, y))
            poly.addContour(pts, is_clockwise(pts))
    return poly


def is_clockwise(pts):
    """
    returns true if a given polygon is in clockwise order
    """
    s = 0
    for i in range(len(pts) - 1):
        if 'x' in pts[i]:
            x1 = pts[i].x
            y1 = pts[i].y
            x2 = pts[i + 1].x
            y2 = pts[i + 1].y
        else:
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
        s += (x2 - x1) * (y2 + y1)
    return s >= 0
