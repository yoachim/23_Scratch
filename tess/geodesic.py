import math
import fractions
import numpy as np
from rubin_sim.utils import ra_dec_from_xyz

# Adapted from https://github.com/antiprism/antiprism_python/blob/master/anti_lib_progs/geodesic.py

# Copyright (c) 2003-2016 Adrian Rossiter <adrian@antiprism.com>
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


class Vec:
    def __init__(self, *v):
        self.v = list(v)

    def fromlist(self, v):
        if not isinstance(v, list):
            raise TypeError
        self.v = v[:]
        return self

    def copy(self):
        return Vec().fromlist(self.v)

    def __str__(self):
        return '(' + repr(self.v)[1:-1] + ')'

    def __repr__(self):
        return 'Vec(' + repr(self.v)[1:-1] + ')'

    def __len__(self):
        return len(self.v)

    def __getitem__(self, key):
        if not isinstance(key, int):
            raise TypeError
        if key < 0 or key >= len(self.v):
            raise KeyError
        return self.v[key]

    def __setitem__(self, key, value):
        if not isinstance(key, int):
            raise TypeError
        if key < 0 or key >= len(self.v):
            raise KeyError
        self.v[key] = value

    # Element-wise negation
    def __neg__(self):
        v = list(map(lambda x: -x, self.v))
        return Vec().fromlist(v)

    # Element-wise addition
    def __add__(self, other):
        v = list(map(lambda x, y: x+y, self.v, other.v))
        return Vec().fromlist(v)

    # Element-wise subtraction
    def __sub__(self, other):
        v = list(map(lambda x, y: x-y, self.v, other.v))
        return Vec().fromlist(v)

    # Element-wise multiplication by scalar
    def __mul__(self, scalar):
        v = list(map(lambda x: x*scalar, self.v))
        return Vec().fromlist(v)

    # Element-wise pre-multiplication by scalar
    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    # Element-wise division by scalar
    def __truediv__(self, scalar):
        return self.__mul__(1/scalar)

    # Vector magnitude/length squared
    def mag2(self):
        return self.dot(self, self)

    # Vector magnitude/length
    def mag(self):
        return math.sqrt(self.mag2())

    # Vector as unit
    def unit(self):
        return self.__truediv__(self.mag())

    # Vector rotated about z-axis
    def rot_z(self, ang):
        r = math.sqrt(self.v[0]**2+self.v[1]**2)
        initial_ang = math.atan2(self.v[1], self.v[0])
        final_ang = initial_ang + ang
        return Vec(r*math.cos(final_ang), r*math.sin(final_ang), self.v[2])

    # Cross product v0 x v1
    @staticmethod
    def cross(v0, v1):
        return Vec(v1[2]*v0[1] - v1[1]*v0[2],
                   v1[0]*v0[2] - v1[2]*v0[0],
                   v1[1]*v0[0] - v1[0]*v0[1])

    # Dot product v0 . v1
    @staticmethod
    def dot(v0, v1):
        return sum(map(lambda x, y: x*y, v0.v, v1.v))

    # Triple product v0. (v1 x v2)
    @staticmethod
    def triple(v0, v1, v2):
        return Vec.dot(v0, Vec.cross(v1, v2))

def get_octahedron(verts, faces):
    """Return an octahedron"""
    X = 0.25 * math.sqrt(2)
    verts.extend([Vec(0.0, 0.5, 0.0), Vec(X, 0.0, -X),
                  Vec(X, 0.0, X), Vec(-X, 0.0, X),
                  Vec(-X, 0.0, -X), Vec(0.0, -0.5, 0.0)])

    faces.extend([(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1),
                  (5, 2, 1), (2, 5, 3), (3, 5, 4), (4, 5, 1)])


def get_tetrahedron(verts, faces):
    """Return an tetrahedron"""
    X = 1 / math.sqrt(3)
    verts.extend([Vec(-X, X, -X), Vec(-X, -X, X),
                  Vec(X, X, X), Vec(X, -X, -X)])
    faces.extend([(0, 1, 2), (0, 3, 1), (0, 2, 3), (2, 1, 3)])


def get_ico_coords():
    """Return icosahedron coordinate values"""
    phi = (math.sqrt(5) + 1) / 2
    rad = math.sqrt(phi+2)
    return 1/rad, phi/rad


def get_triangle(verts, faces):
    """Return an triangle"""
    if 1:
        Y = math.sqrt(3.0) / 12.0
        Z = -0.8
        verts.extend([Vec(-0.25, -Y, Z), Vec(0.25, -Y, Z),
                      Vec(0.0, 2 * Y, Z)])
        faces.extend([(0, 1, 2)])
    else:
        X, Z = get_ico_coords()
        verts.extend([Vec(-X, 0.0, -Z), Vec(X, 0.0, -Z),
                      Vec(0.0, Z, -X), Vec(0.0, -Z, -X)])
        faces.extend([(0, 1, 2), (0, 3, 1)])


def get_icosahedron(verts, faces):
    """Return an icosahedron"""
    X, Z = get_ico_coords()
    verts.extend([Vec(-X, 0.0, Z), Vec(X, 0.0, Z), Vec(-X, 0.0, -Z),
                  Vec(X, 0.0, -Z), Vec(0.0, Z, X), Vec(0.0, Z, -X),
                  Vec(0.0, -Z, X), Vec(0.0, -Z, -X), Vec(Z, X, 0.0),
                  Vec(-Z, X, 0.0), Vec(Z, -X, 0.0), Vec(-Z, -X, 0.0)])

    faces.extend([(0, 4, 1), (0, 9, 4), (9, 5, 4), (4, 5, 8), (4, 8, 1),
                  (8, 10, 1), (8, 3, 10), (5, 3, 8), (5, 2, 3), (2, 7, 3),
                  (7, 10, 3), (7, 6, 10), (7, 11, 6), (11, 0, 6), (0, 1, 6),
                  (6, 1, 10), (9, 0, 11), (9, 11, 2), (9, 2, 5), (7, 2, 11)])


def get_poly(poly, verts, edges, faces):
    """Return the base polyhedron"""
    if poly == 'i':
        get_icosahedron(verts, faces)
    elif poly == 'o':
        get_octahedron(verts, faces)
    elif poly == 't':
        get_tetrahedron(verts, faces)
    elif poly == 'T':
        get_triangle(verts, faces)
    else:
        return 0

    for face in faces:
        for i in range(0, len(face)):
            i2 = i + 1
            if(i2 == len(face)):
                i2 = 0

            if face[i] < face[i2]:
                edges[(face[i], face[i2])] = 0
            else:
                edges[(face[i2], face[i])] = 0

    return 1


def grid_to_points(grid, freq, div_by_len, f_verts, face):
    """Convert grid coordinates to Cartesian coordinates"""
    points = []
    v = []
    for vtx in range(3):
        v.append([Vec(0.0, 0.0, 0.0)])
        edge_vec = f_verts[(vtx + 1) % 3] - f_verts[vtx]
        if div_by_len:
            for i in range(1, freq + 1):
                v[vtx].append(edge_vec * float(i) / freq)
        else:
            ang = 2 * math.asin(edge_vec.mag() / 2.0)
            unit_edge_vec = edge_vec.unit()
            for i in range(1, freq + 1):
                len = math.sin(i * ang / freq) / \
                    math.sin(math.pi / 2 + ang / 2 - i * ang / freq)
                v[vtx].append(unit_edge_vec * len)

    for (i, j) in grid.values():

        if (i == 0) + (j == 0) + (i + j == freq) == 2:   # skip vertex
            continue
        # skip edges in one direction
        if (i == 0 and face[2] > face[0]) or (
                j == 0 and face[0] > face[1]) or (
                i + j == freq and face[1] > face[2]):
            continue

        n = [i, j, freq - i - j]
        v_delta = (v[0][n[0]] + v[(0-1) % 3][freq - n[(0+1) % 3]] -
                   v[(0-1) % 3][freq])
        pt = f_verts[0] + v_delta
        if not div_by_len:
            for k in [1, 2]:
                v_delta = (v[k][n[k]] + v[(k-1) % 3][freq - n[(k+1) % 3]] -
                           v[(k-1) % 3][freq])
                pt = pt + f_verts[k] + v_delta
            pt = pt / 3
        points.append(pt)

    return points


def make_grid(freq, m, n):
    """Make the geodesic pattern grid"""
    grid = {}
    rng = (2 * freq) // (m + n)
    for i in range(rng):
        for j in range(rng):
            x = i * (-n) + j * (m + n)
            y = i * (m + n) + j * (-m)

            if x >= 0 and y >= 0 and x + y <= freq:
                grid[(i, j)] = (x, y)

    return grid


def geo(repeats=1, polyhedron="i", class_pattern=[1, 0, 1],
        flat_faced=False, equal_length=True, to_ra_dec=True):
    """
    Parameters
    ----------
    repeats : int (1)
        Number of times the pattern is repeated. Default 1
    polyhedron : str ("i")
        base polyhedron: "i" - icosahedron (default), "o" - octahedron,
        "t" - tetrahedron, "T" - triangle.
    class_pattern : list of int ([1, 0, 1])
        class of face division,  1 (Class I, default) or 
        2 (Class II), or two numbers separated by a comma to
        determine the pattern (Class III generally, but 1,0 is 
        Class I, 1,1 is Class II, etc).
    flat_faced : bool (False)
        Keep flat-faced polyhedron rather than projecting
        the points onto a sphere.
    equal_length : bool (True)
        Divide the edges by equal lengths rather than equal angles
    to_ra_dec : bool (True)
        Convert from x,y,z coordinates to RA,dec in degrees.
        Default True
    """
    verts = []
    edges = {}
    faces = []
    get_poly(polyhedron, verts, edges, faces)

    (M, N, reps) = class_pattern
    repeats = repeats * reps
    freq = repeats * (M**2 + M*N + N**2)

    grid = {}
    grid = make_grid(freq, M, N)

    points = verts
    for face in faces:
        if polyhedron == 'T':
            face_edges = (0, 0, 0)  # generate points for all edges
        else:
            face_edges = face
        points[len(points):len(points)] = grid_to_points(
            grid, freq, equal_length,
            [verts[face[i]] for i in range(3)], face_edges)

    if not flat_faced:
        points = [p.unit() for p in points]  # Project onto sphere

    if to_ra_dec:
        points = np.vstack([ra_dec_from_xyz(p[0], p[1], p[2]) for p in points])

    return points



# https://github.com/antiprism/antiprism_python/blob/master/anti_lib_progs/sph_spiral.py

def angle_to_point(a, number_turns):
    a2 = 2 * a * number_turns   # angle turned around y axis
    r = math.sin(a)             # distance from y axis
    y = math.cos(a)
    x = r * math.sin(a2)
    z = r * math.cos(a2)
    return Vec(x, y, z)


# binary search for angle with distance rad from point with angle a0
def psearch(a1_delt, a1, a0, rad, number_turns):
    a_test = a1_delt + (a1 - a1_delt) / 2.0
    dist = (angle_to_point(a_test, number_turns) -
            angle_to_point(a0, number_turns)).mag()
    eps = 1e-5
    if rad + eps > dist > rad - eps:
        return a_test
    elif rad < dist:      # Search in first interval
        return psearch(a1_delt, a_test, a0, rad, number_turns)
    else:                 # Search in second interval
        return psearch(a_test, a1, a0, rad, number_turns)


def calc_points(number_turns=10, distance_between_points=None):
    points = []
    number_turns = number_turns
    if not number_turns:
        number_turns = 1e-12
    if distance_between_points:
        rad = 2*distance_between_points
    else:
        # half distance between turns on a rad 1 sphere
        rad = 2*math.sqrt(1 - math.cos(math.pi/(number_turns-1)))
    a0 = 0
    cur_point = Vec(0.0, 1.0, 0.0)
    points.append(cur_point)

    delt = math.atan(rad / 2) / 10
    a1 = a0 + .0999999 * delt                        # still within sphere
    while a1 < math.pi:
        if (cur_point - angle_to_point(a1, number_turns)).mag() > rad:
            a0 = psearch(a1 - delt, a1, a0, rad, number_turns)
            cur_point = angle_to_point(a0, number_turns)
            points.append(cur_point)
            a1 = a0

        a1 += delt

    points = np.vstack([ra_dec_from_xyz(p[0], p[1], p[2]) for p in points])
    
    return points
