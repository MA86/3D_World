from __future__ import annotations
import OpenGL.GL as GL
import ctypes


class VertexArray:
    """
    This class encapsulates a mesh (AKA model).
    """

    def __init__(self, vertices: ctypes.Array, num_verts: int, indices: ctypes.Array, num_indices: int) -> None:
        # Number of vertices & indices in the buffers
        self._m_num_verts: int = num_verts
        self._m_num_indices: int = num_indices
        # OpenGL IDs of the buffers
        self._m_vertex_buffer_id: ctypes.c_uint = ctypes.c_uint(0)
        self._m_index_buffer_id: ctypes.c_uint = ctypes.c_uint(0)
        # OpenGL ID of VertexArray object
        self._m_vertex_array_id: ctypes.c_uint = ctypes.c_uint(0)

        # Create a GL vertex array object (GL returns ID not ref to object!)
        GL.glGenVertexArrays(1, ctypes.byref(self._m_vertex_array_id))
        GL.glBindVertexArray(self._m_vertex_array_id)

        # Create vertex buffer, copy vertices to it
        GL.glGenBuffers(1, ctypes.byref(self._m_vertex_buffer_id))
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._m_vertex_buffer_id)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self._m_num_verts *
                        8 * ctypes.sizeof(ctypes.c_float), vertices, GL.GL_STATIC_DRAW)
        # Create index buffer, copy indices to it
        GL.glGenBuffers(1, ctypes.byref(self._m_index_buffer_id))
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self._m_index_buffer_id)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self._m_num_indices *
                        ctypes.sizeof(ctypes.c_uint), indices, GL.GL_STATIC_DRAW)

        # Identify attributes in the vertex array (pos, normal, texture coord.)
        # Position attribute
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(
            0, 3, GL.GL_FLOAT, GL.GL_FALSE,
            ctypes.sizeof(ctypes.c_float) * 8,  # Stride is 5 floats
            None)
        # Normal attribute
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(
            1, 3, GL.GL_FLOAT, GL.GL_FALSE,
            ctypes.sizeof(ctypes.c_float) * 8,
            ctypes.c_void_p(ctypes.sizeof(ctypes.c_float) * 3))  # Offset is 3 floats from start
        # Texture coord. attribute
        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, GL.GL_FALSE, ctypes.sizeof(
            ctypes.c_float) * 8, ctypes.c_void_p(ctypes.sizeof(ctypes.c_float) * 6))

    def delete(self) -> None:
        # Delete in reverse
        GL.glDeleteBuffers(1, ctypes.byref(self._m_vertex_buffer_id))
        GL.glDeleteBuffers(1, ctypes.byref(self._m_index_buffer_id))
        GL.glDeleteVertexArrays(1, ctypes.byref(self._m_vertex_array_id))

    # Which vertex array object to use
    def set_active(self) -> None:
        GL.glBindVertexArray(self._m_vertex_array_id)

    def get_num_indices(self) -> int:
        return self._m_num_indices

    def get_num_vertices(self) -> int:
        return self._m_num_verts
