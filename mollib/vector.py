"""
Module for handling 3d vectors.
"""

import numpy as np


class Vector:
    """
    Vector is a class to handle 3d vectors of floats.
    The coordinates are accessible via properties x, y, z.
    """

    def __init__(self, *args):
        # Vector() can be initialized with 0, 1 or 3 arguments
        if args:

            # one argument
            if len(args) == 1:
                arg = args[0]
                try:
                    # initialize vector from iterable
                    self.__data = np.array(arg, dtype=float)
                    if self.__data.shape != (3, ):
                        raise ValueError
                except ValueError:
                    # initialize vector from space-/comma-separated string
                    words = arg.replace(',', ' ').split()
                    self.__data = np.array(words, dtype=float)

            # three arguments
            elif len(args) == 3:
                # initialize vector from list of args
                self.__data = np.array(args, dtype=float)
            else:
                raise TypeError('Invalid number of arguments for Vector()')

        # zero arguments
        else:
            self.__data = np.array([0., 0., 0.])

    @property
    def x(self):
        return self.__data[0]

    @x.setter
    def x(self, value):
        self.__data[0] = value

    @property
    def y(self):
        return self.__data[1]

    @y.setter
    def y(self, value):
        self.__data[1] = value

    @property
    def z(self):
        return self.__data[2]

    @z.setter
    def z(self, value):
        self.__data[2] = value

    def __str__(self):
        return f'{self.x:8.3f}{self.y:8.3f}{self.z:8.3f}'

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __pos__(self):
        return Vector(self.x, self.y, self.z)

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __mul__(self, factor):
        return Vector(self.x * factor, self.y * factor, self.z * factor)

    def __rmul__(self, factor):
        return self * factor

    def __div__(self, factor):
        return self * (1.0 / factor)

    def dot(self, other):
        """Dot product of two vectors"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        """Cross product of two vectors"""
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    @property
    def mod2(self):
        """|vector|^2"""
        return self.dot(self)

    @property
    def length(self):
        """Returns vector's length"""
        return self.mod2 ** 0.5

    @property
    def norm(self):
        """Returns normalized vector"""
        return self.__div__(self.length)

    def __iadd__(self, other):
        """Addition assignment"""
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __isub__(self, other):
        """Subtraction assignment"""
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __imul__(self, factor):
        """Scalar multiplication assignment"""
        self.x *= factor
        self.y *= factor
        self.z *= factor
        return self

    def __idiv__(self, factor):
        """Scalar division assignment"""
        self.x /= factor
        self.y /= factor
        self.z /= factor
        return self

    @property
    def numpy(self):
        """Reference to numpy array"""
        return self.__data

    @property
    def random(self):
        """Returns random normalized vector from spherical uniform distribution"""
        phi = np.random.uniform(0., 2. * np.pi)
        cos_theta = np.random.uniform(-1., 1.)
        sin_theta = np.sqrt(1. - cos_theta ** 2)
        self.x = sin_theta * np.cos(phi)
        self.y = sin_theta * np.sin(phi)
        self.z = cos_theta
        return self
