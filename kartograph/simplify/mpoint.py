

class MPoint:
    """
    Point class used for polygon simplification
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.simplified = False
        self.deleted = False
        self.keep = False
        self.features = set()

    def isDeletable(self):
        if self.keep or self.simplified or self.three:
            return False
        return True

    def __repr__(self):
        return 'Pt(%.2f,%.2f)' % (self.x, self.y)

    def __len__(self):
        return 2

    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise IndexError()

    def __contains__(self, key):
        if key == "deleted":
            return True
        return False
