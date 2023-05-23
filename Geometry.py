class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.coord = (x, y)
        self.incident = None

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Half_Edge:
    def __init__(
        self, origin, twin=None, next_edge=None, prev_edge=None, face=None, layer=None
    ):
        self.origin = origin
        self.twin = twin
        self.next = next_edge
        self.prev = prev_edge
        self.face = face
        self.layer = layer

    def __repr__(self):
        return f"Edge from {self.origin} to {self.twin.origin}"


class Face:
    def __init__(self, outer, inner):
        self.outer_component = outer
        self.inner_components = inner

    def __repr__(self) -> str:
        return f"Outer edge {self.outer_component}"


class DCEL:
    def __init__(self):
        self.vertices = []
        self.half_edges = []
        self.faces = []

    def add_vertex(self, vertex):
        self.vertices.append(vertex)
        return vertex

    def add_half_edge(self, half_edge):
        self.half_edges.append(half_edge)
        return half_edge

    def add_face(self, face):
        self.faces.append(face)
        return face

    def split_edge(self, edge, vertex):
        new_edge = Half_Edge(vertex)
        old_edge = edge.twin.prev
        old_edge.next = new_edge

        new_edge.prev = old_edge
        new_edge.next = edge

        edge.origin = vertex
        edge.prev = new_edge

        new_edge.face = old_edge.face
        new_edge.twin = edge
        edge.twin = new_edge

        return new_edge

    def overlay(self, others, intersections):
        for other in others:
            self = self + other
        for intersection in intersections:
            vtx = Vertex(intersection.x, intersection.y)
            # Previous half edges
            e1, e2 = intersection.segment
            # New half edges
            ep11 = Half_Edge(vtx)
            ep12 = Half_Edge(vtx)
            # Twin of e1
            et1 = e1.twin
            # Set twins
            e1.twin = ep11
            ep11.twin = e1
            et1.twin = ep12
            ep12.twin = et1

            # Set next and prev
            ep11.next = et1.next
            et1.next.prev = ep11

            ep12.next = e1.next
            e1.next.prev = ep12

            self.add_half_edge(ep12)
            self.add_half_edge(ep11)
        return self

    def __add__(self, other):
        temp = DCEL()
        temp.vertices += other.vertices
        temp.half_edges += other.half_edges
        temp.faces += other.faces
        return temp

    def __repr__(self) -> str:
        return f"List of edges {self.half_edges}"


# Computational objects
import math
from dataclasses import dataclass


class Segment:
    pass


@dataclass
class Point:
    x: float
    y: float
    segment: Segment = None
    line = None

    def __eq__(self, other) -> bool:
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Line:
    def __init__(self, p1: Point, p2: Point):
        try:
            self.m = (p2.y - p1.y) / (p2.x - p1.x)
        except ZeroDivisionError:
            self.m = math.inf
        if self.m != math.inf:
            self.b = p1.y - self.m * p1.x
        else:
            self.b = p1.x
            if (p2.y - p1.y) > 0:
                self.m = 10000000000000
            else:
                self.m = -10000000000000


class Segment:
    def __init__(self, p1, p2, line=None, name=None, layer=None, edges=None):
        if p1.y < p2.y:
            p1, p2 = p2, p1
        self.p1 = p1
        self.p2 = p2
        # self.linename = lineName
        self.line = line
        self.key = None
        if not line:
            self.line = Line(p1, p2)
        self.name = name
        self.up = None
        self.down = None
        self.layer = layer
        self.edges = edges

    def intersect(self, other) -> Point:
        if self.line.m == other.line.m and self.line.b == other.line.b:
            return None

        if other.p2.x == math.inf:
            if self.line.m != math.inf:
                x = (other.p2.y - self.line.b) / self.line.m
            else:
                x = self.p1.x
            return Point(x, other.p2.y, self)

        c = self.p1.y - self.line.m * self.p1.x
        f = other.p1.y - other.line.m * other.p1.x
        a, b = self.line.m, -1
        (
            d,
            e,
        ) = (
            other.line.m,
            -1,
        )
        x = 0
        y = 0
        try:
            x = (-c * e - -f * b) / (a * e - d * b)
            y = (a * -f - d * -c) / (a * e - d * b)
        except:
            return None

        p = Point(x, y, [self.edges, other.edges])
        e = 0.000001
        if (
            min(self.p1.x, self.p2.x) <= p.x + e
            and p.x - e <= max(self.p1.x, self.p2.x)
            and min(self.p1.y, self.p2.y) <= p.y + e
            and p.y - e <= max(self.p1.y, self.p2.y)
        ):
            if (
                min(other.p1.x, other.p2.x) <= p.x + e
                and p.x - e <= max(other.p1.x, other.p2.x)
                and min(other.p1.y, other.p2.y) <= p.y + e
                and p.y - e <= max(other.p1.y, other.p2.y)
            ):
                return p
        return None

    def get_x(self, y: int):
        try:
            return (y - self.b) / self.m
        except ZeroDivisionError:
            return math.inf

    def __eq__(self, other):
        if (self.p1 == other.p1 and self.p2 == other.p2) or (
            self.p2 == other.p1 and self.p1 == other.p2
        ):
            return True
        return False

    def __repr__(self):
        return f"Segment {self.name}"


def calcIntersections(layers):
    segments = []
    for l in layers:
        for edge in l.half_edges:
            partner = edge.twin
            p1 = Point(edge.origin.x, edge.origin.y)
            p2 = Point(partner.origin.x, partner.origin.y)
            segments.append(Segment(p1, p2, layer=edge.layer, edges=edge))
    intersections = []

    segments = set(segments)
    segments = list(segments)

    while segments:
        actualSeg = segments.pop()
        for seg in segments:
            inter = actualSeg.intersect(seg)
            if (
                inter
                and (inter not in intersections)
                and (actualSeg.layer != seg.layer)
            ):
                intersections.append(inter)
    return intersections
