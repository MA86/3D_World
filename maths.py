from __future__ import annotations
import math
import ctypes

""" This Global Namespace contain useful math variables, functions, and classes """


### Math constants ###
PI = math.pi
TWO_PI = math.pi * 2.0
PI_OVER_TWO = math.pi / 2.0
POS_INFINITY = math.inf
NEG_INFINITY = -math.inf


### Math functions ###


def to_radians(degrees: float) -> float:
    return degrees * PI / 180.0


def to_degrees(radians: float) -> float:
    return radians * 180.0 / PI


def check_near_zero(value: float, epsilon: float = 0.001) -> bool:
    if abs(value) <= epsilon:
        return True
    else:
        return False


def absolute_value(value: float) -> float:
    return abs(value)


def clamp(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


def lerp(a: float, b: float, f: float) -> float:
    return a + f * (b - a)


def cos(angle: float) -> float:
    return math.cos(angle)


def sin(angle: float) -> float:
    return math.sin(angle)


def tan(angle: float) -> float:
    return math.tan(angle)


def atan2(y: float, x: float) -> float:
    return math.atan2(y, x)


### Math classes ###


class Vector2D:
    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x: float = x
        self.y: float = y

    def set(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Vector2D) -> Vector2D:
        if isinstance(other, Vector2D):
            # Two vectors
            return Vector2D(self.x * other.x, self.y * other.y)
        elif isinstance(other, float):
            # Vector and scalar
            return Vector2D(self.x * other, self.y * other)
        else:
            raise NotImplementedError()

    # Alternative to length()
    def length_sq(self) -> float:
        return (self.x * self.x + self.y * self.y)

    def length(self) -> float:
        return math.sqrt(self.length_sq())

    def normalize(self) -> None:
        length: float = self.length()
        self.x /= length
        self.y /= length

    @staticmethod
    def dot(a: Vector2D, b: Vector2D) -> float:
        return (a.x * b.x + a.y * b.y)

    @staticmethod
    def lerp(a: Vector2D, b: Vector2D, f: float) -> Vector2D:
        # TODO: Untested!
        return (a + ((b - a) * f))

    # Reflect V about N
    @staticmethod
    def reflect(v: Vector2D, n: Vector2D) -> Vector2D:
        return v - 2.0 * Vector2D.dot(v, n) * n

    # Transform vector by matrix
    # [In homogenous coordinate system, vector must have n+1 components, so use w.]
    # [It's because transformation matrix (for move) must be 3x3!]
    @staticmethod
    def transform(vec: Vector2D, mat: Matrix3, w: float = 1.0) -> Vector2D:
        ret_val: Vector2D = Vector2D()
        ret_val.x = vec.x * mat.mat[0][0] + \
            vec.y * mat.mat[1][0] + w * mat.mat[2][0]
        ret_val.y = vec.x * mat.mat[0][1] + \
            vec.y * mat.mat[1][1] + w * mat.mat[2][1]
        # Ignore w since we are not returning a new value for it
        return ret_val


class Vector3D:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x: float = x
        self.y: float = y
        self.z: float = z

    def set(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    # Addition
    def __add__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    # Subtraction
    def __sub__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    # Component-wise multiplication
    def __mul__(self, other: Vector3D) -> Vector3D:
        if isinstance(other, Vector3D):
            # Two vectors
            return Vector3D(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, float):
            # Vector and scalar
            return Vector3D(self.x * other, self.y * other, self.z * other)
        else:
            raise NotImplementedError()

    # Alternative to length()
    def length_sq(self) -> float:
        return (self.x * self.x + self.y * self.y + self.z * self.z)

    # Length of vector
    def length(self) -> float:
        return math.sqrt(self.length_sq())

    def normalize(self) -> None:
        length: float = self.length()
        self.x /= length
        self.y /= length
        self.z /= length

    # Dot product between vectors
    @staticmethod
    def dot(a: Vector3D, b: Vector3D) -> float:
        return (a.x * b.x + a.y * b.y + a.z * b.z)

    # Cross product between vectors
    @staticmethod
    def cross(a: Vector3D, b: Vector3D) -> Vector3D:
        v: Vector3D = Vector3D()
        v.x = a.y * b.z - a.z * b.y
        v.y = a.z * b.x - a.x * b.z
        v.z = a.x * b.y - a.y * b.x
        return v

    # Lerp from a to b by f
    @staticmethod
    def lerp(a: Vector3D, b: Vector3D, f: float) -> Vector3D:
        # TODO: Untested!
        return (a + ((b - a) * f))

    # Reflect v about n
    @staticmethod
    def reflect(v: Vector3D, n: Vector3D) -> Vector3D:
        return v - 2.0 * Vector3D.dot(v, n) * n

    # Transform vector by matrix
    # [Technically you can argue that we don't need n+1 component here, but you are wrong!]
    # [You need it at least for moving ORIGIN! Ex., [0, 0, 0] x T = [0, 0, 0], not useful!]
    @staticmethod
    def transform(vec: Vector3D, mat: Matrix4, w: float = 1.0) -> Vector3D:
        ret_val: Vector3D = Vector3D()
        ret_val.x = vec.x * mat.mat[0][0] + \
            vec.y * mat.mat[1][0] + vec.z * mat.mat[2][0] + w * mat.mat[3][0]
        ret_val.y = vec.x * mat.mat[0][1] + \
            vec.y * mat.mat[1][1] + vec.z * mat.mat[2][1] + w * mat.mat[3][1]
        ret_val.z = vec.x * \
            mat.mat[0][2] + vec.y * mat.mat[1][2] + \
            vec.z * mat.mat[2][2] + w * mat.mat[3][2]
        # Ignore w since we are not returning a new value for it
        return ret_val

    # Transform vector by matrix and renormalize w
    @staticmethod
    def transform_with_persp_div(vec: Vector3D, mat: Matrix4, w: float = 1.0):
        # TODO
        raise NotImplementedError()

    # Transform vector by quaternion
    @staticmethod
    def transform_q(vec: Vector3D, q: Quaternion) -> Vector3D:
        # TODO
        raise NotImplementedError()


# 4x4 Matrix
# [No need to define 3x3 Matrix because OpenGL vertex layout]
# [uses 4D vectors for everthing]
class Matrix4:
    def __init__(self) -> None:
        # C array storing matrix data
        CArray = ((ctypes.c_float * 4) * 4)
        self.m_mat = CArray()

        # Initialize array to identity matrix
        self.m_mat[0][0] = 1.0
        self.m_mat[0][1] = 0.0
        self.m_mat[0][2] = 0.0
        self.m_mat[0][3] = 0.0

        self.m_mat[1][0] = 0.0
        self.m_mat[1][1] = 1.0
        self.m_mat[1][2] = 0.0
        self.m_mat[1][3] = 0.0

        self.m_mat[2][0] = 0.0
        self.m_mat[2][1] = 0.0
        self.m_mat[2][2] = 1.0
        self.m_mat[2][3] = 0.0

        self.m_mat[3][0] = 0.0
        self.m_mat[3][1] = 0.0
        self.m_mat[3][2] = 0.0
        self.m_mat[3][3] = 1.0

    # Matrix multiplication
    def __mul__(self, other: Matrix4) -> Matrix4:
        ret_val: Matrix4 = Matrix4()

        # Row 0
        ret_val.m_mat[0][0] = self.m_mat[0][0] * other.m_mat[0][0] + self.m_mat[0][1] * \
            other.m_mat[1][0] + self.m_mat[0][2] * \
            other.m_mat[2][0] + self.m_mat[0][3] * other.m_mat[3][0]

        ret_val.m_mat[0][1] = self.m_mat[0][0] * other.m_mat[0][1] + self.m_mat[0][1] * \
            other.m_mat[1][1] + self.m_mat[0][2] * \
            other.m_mat[2][1] + self.m_mat[0][3] * other.m_mat[3][1]

        ret_val.m_mat[0][2] = self.m_mat[0][0] * other.m_mat[0][2] + self.m_mat[0][1] * \
            other.m_mat[1][2] + self.m_mat[0][2] * \
            other.m_mat[2][2] + self.m_mat[0][3] * other.m_mat[3][2]

        ret_val.m_mat[0][3] = self.m_mat[0][0] * other.m_mat[0][3] + self.m_mat[0][1] * \
            other.m_mat[1][3] + self.m_mat[0][2] * \
            other.m_mat[2][3] + self.m_mat[0][3] * other.m_mat[3][3]

        # Row 1
        ret_val.m_mat[1][0] = self.m_mat[1][0] * other.m_mat[0][0] + self.m_mat[1][1] * \
            other.m_mat[1][0] + self.m_mat[1][2] * \
            other.m_mat[2][0] + self.m_mat[1][3] * other.m_mat[3][0]

        ret_val.m_mat[1][1] = self.m_mat[1][0] * other.m_mat[0][1] + self.m_mat[1][1] * \
            other.m_mat[1][1] + self.m_mat[1][2] * \
            other.m_mat[2][1] + self.m_mat[1][3] * other.m_mat[3][1]

        ret_val.m_mat[1][2] = self.m_mat[1][0] * other.m_mat[0][2] + self.m_mat[1][1] * \
            other.m_mat[1][2] + self.m_mat[1][2] * \
            other.m_mat[2][2] + self.m_mat[1][3] * other.m_mat[3][2]

        ret_val.m_mat[1][3] = self.m_mat[1][0] * other.m_mat[0][3] + self.m_mat[1][1] * \
            other.m_mat[1][3] + self.m_mat[1][2] * \
            other.m_mat[2][3] + self.m_mat[1][3] * other.m_mat[3][3]

        # Row 2
        ret_val.m_mat[2][0] = self.m_mat[2][0] * other.m_mat[0][0] + self.m_mat[2][1] * \
            other.m_mat[1][0] + self.m_mat[2][2] * \
            other.m_mat[2][0] + self.m_mat[2][3] * other.m_mat[3][0]

        ret_val.m_mat[2][1] = self.m_mat[2][0] * other.m_mat[0][1] + self.m_mat[2][1] * \
            other.m_mat[1][1] + self.m_mat[2][2] * \
            other.m_mat[2][1] + self.m_mat[2][3] * other.m_mat[3][1]

        ret_val.m_mat[2][2] = self.m_mat[2][0] * other.m_mat[0][2] + self.m_mat[2][1] * \
            other.m_mat[1][2] + self.m_mat[2][2] * \
            other.m_mat[2][2] + self.m_mat[2][3] * other.m_mat[3][2]

        ret_val.m_mat[2][3] = self.m_mat[2][0] * other.m_mat[0][3] + self.m_mat[2][1] * \
            other.m_mat[1][3] + self.m_mat[2][2] * \
            other.m_mat[2][3] + self.m_mat[2][3] * other.m_mat[3][3]

        # Row 3
        ret_val.m_mat[3][0] = self.m_mat[3][0] * other.m_mat[0][0] + self.m_mat[3][1] * \
            other.m_mat[1][0] + self.m_mat[3][2] * \
            other.m_mat[2][0] + self.m_mat[3][3] * other.m_mat[3][0]

        ret_val.m_mat[3][1] = self.m_mat[3][0] * other.m_mat[0][1] + self.m_mat[3][1] * \
            other.m_mat[1][1] + self.m_mat[3][2] * \
            other.m_mat[2][1] + self.m_mat[3][3] * other.m_mat[3][1]

        ret_val.m_mat[3][2] = self.m_mat[3][0] * other.m_mat[0][2] + self.m_mat[3][1] * \
            other.m_mat[1][2] + self.m_mat[3][2] * \
            other.m_mat[2][2] + self.m_mat[3][3] * other.m_mat[3][2]

        ret_val.m_mat[3][3] = self.m_mat[3][0] * other.m_mat[0][3] + self.m_mat[3][1] * \
            other.m_mat[1][3] + self.m_mat[3][2] * \
            other.m_mat[2][3] + self.m_mat[3][3] * other.m_mat[3][3]

        return ret_val

    # Create a scale matrix with x, y, and z scales
    @staticmethod
    def create_scale_matrix_xyz(xscale: float, yscale: float, zscale: float) -> Matrix4:
        temp: Matrix4 = Matrix4()

        temp.m_mat[0][0] = xscale
        temp.m_mat[1][1] = yscale
        temp.m_mat[2][2] = zscale
        temp.m_mat[3][3] = 1.0

        return temp

    # Create a scale matrix with uniform factor
    @staticmethod
    def create_scale_matrix_uniform(scale: float) -> Matrix4:
        return Matrix4.create_scale_matrix_xyz(scale, scale, scale)

    # TODO Create rotation matrix about x-axis
    # TODO Create rotation matrix about y-axix

    # Create rotation matrix about z-axis
    @staticmethod
    def create_rotation_matrix_z(theta: float) -> Matrix4:
        temp: Matrix4 = Matrix4()

        temp.m_mat[0][0] = cos(theta)
        temp.m_mat[0][1] = sin(theta)
        temp.m_mat[1][0] = -sin(theta)
        temp.m_mat[1][1] = cos(theta)
        temp.m_mat[2][2] = 1.0
        temp.m_mat[3][3] = 1.0

        return temp

    # Create translation matrix
    @staticmethod
    def create_translation_matrix(trans: Vector3D) -> Matrix4:
        temp: Matrix4 = Matrix4()

        temp.m_mat[0][0] = 1.0
        temp.m_mat[1][1] = 1.0
        temp.m_mat[2][2] = 1.0
        temp.m_mat[3][0] = trans.x
        temp.m_mat[3][1] = trans.y
        temp.m_mat[3][2] = trans.z
        temp.m_mat[3][3] = 1.0

        return temp

    # Create a 'simple' view-proj matrix
    @staticmethod
    def create_simple_view_proj(width: float, height: float) -> Matrix4:
        temp: Matrix4 = Matrix4()

        temp.m_mat[0][0] = 2.0 / width
        temp.m_mat[1][1] = 2.0 / height
        temp.m_mat[2][2] = 1.0
        temp.m_mat[3][2] = 1.0
        temp.m_mat[3][3] = 1.0

        return temp

    # TODO, add additional matrix4 operations
