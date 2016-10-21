#!/usr/bin/env python

##
# \file space.py
#
# Contains classes that describe point rectangles
# in a 2D space

import math

class Point(object):
    
    ##
    # init a point in 2D space
    #
    # \param x an   x-coordinate (also specify y)
    # \param y      an y-coordinate (also specify x)
    # \param tup    a tuple with an x and y coordinate
    def __init__(self, x=None, y=None, tup=None):
        if x != None and y != None:
            self.x, self.y = x, y
        elif tup:
            self.x, self.y = tuple(tup)
        else:
            raise ValueError("To init a Point specify x and y or tup")
    
    ##
    # return the distance between two points
    def distance(p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def __str__(self):
        return str((self.x, self.y))


if __name__ == "__main__":
    p1 = Point(x=0.0, y=0.0)
    t = (4.0, 5.0)
    p2 = Point(tup=t)
    print "The distance between ", p1, "and ", p2, " = ", Point.distance(p1, p2)
