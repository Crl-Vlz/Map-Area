class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.coord = (x, y)
        self.incident = None

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Half_Edge:
    def __init__(self, origin, twin=None, next_edge=None, prev_edge=None, face=None):
        self.origin = origin
        self.twin = twin
        self.next = next_edge
        self.prev = prev_edge
        self.face = face

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

    def __repr__(self) -> str:
        return f"List of edges {self.half_edges}"
