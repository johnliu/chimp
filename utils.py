"""
Utility classes and methods.
"""
from collections import namedtuple


Point = namedtuple('Point', ['x', 'y'])


class Rect(object):
    def __init__(self, *args):
        """
        Rect(a, b) - construct a rectangle with two points.
        Rect(x1, y1, x2, y2) - construct a rectangle with coordinates.
        """
        if len(args) == 4:
            a = Point(args[0], args[1])
            b = Point(args[2], args[3])
        if len(args) == 2:
            a = args[0]
            b = args[1]

        self.a = a
        self.b = b

    def contains(self, p):
        return self.a.x <= p.x and self.b.x >= p.x and self.a.y <= p.y and self.b.y >= p.y

    def __contains__(self, item):
        return self.contains(item)

    def __repr__(self):
        return '%s -> %s' % (self.a, self.b)

