
from bbox import BBox
from geometry import Geometry


class Line(Geometry):
    """
    simple line (= list of points)
    """
    def __init__(self, points):
        self.pts = points
        
    def bbox(self):
        """
        returns the bounding box of the line
        """
        bbox = BBox()
        for pt in self.pts:
            bbox.update(pt)
        return bbox
    
    def project(self, proj):
        """
        projects the line to a map projection
        """
        pts = []
        for pt in self.pts:
            p = proj.project(pt[0], pt[1])
            if p is not None:
                pts.append(p)
        return Line(pts)
    
    
    def project_view(self, view):
        """
        transforms the line to a new view
        """
        pts = []
        for pt in self.pts:
            p = view.project(pt)
            pts.append(p)
        return Line(pts)
        
    
    def to_svg(self, svg, round):
        """
        constructs a svg representation of this line
        """
        path_str = ""
        if round is False: fmt = '%f,%f'
        else: 
            fmt = '%.'+str(round)+'f'
            fmt = fmt+','+fmt
        
        for pt in self.pts:
            if path_str == "": path_str = "M"
            else: path_str += "L"
            path_str += fmt % (pt.x, pt.y)
            
        path = svg.node('path', d=path_str)
        return path
        
    
    def crop_to(self, geom):
        # skip
        return self
    
    
    def is_empty(self):
        return len(self.pts) == 0
        
    
    def unify(self, point_store, precision):
        from kartograph.simplify import unify_polygon
        self.pts = unify_polygon(self.pts, point_store, precision)

    
    def points(self):
        return [self.pts]
    
    
    def update(self):
        """
        is called after the points of this geometry have been
        changed from outside this class
        """
        pass
        
        