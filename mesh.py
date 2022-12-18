from __future__ import annotations
import math
import sdl2
import json
import ctypes
from maths import Vector3D
from vertex_array import VertexArray


class Mesh:
    """
    This class simply encapsulates mesh loading from file into VertexArray.
    """

    def __init__(self) -> None:
        # Textures associated with this mesh
        self._m_textures: list = []
        # Vertices associated with this mesh
        self._m_vertex_array: VertexArray = None
        # Name of shader specified by mesh
        self._m_shader_name: str = ""
        # Object space bounding sphere radius
        self._m_radius: float = 0.0
        self._m_spec_power: float = 100.0

    def delete(self) -> None:
        # Nothing to implement
        pass

    # Creates a list of vertices and indices from JSON mesh file
    def load(self, file_name: str, renderer: Renderer) -> bool:
        file_obj = open(file_name, "r")
        if not file_obj:
            sdl2.SDL_Log(b"File not found: ", file_name.encode())
            return False

        data = json.load(file_obj)
        if not data:
            sdl2.SDL_Log(b"Mesh is not valid JSON: ", file_name.encode())
            return False

        if data["version"] != 1:
            sdl2.SDL_Log(b"Mesh is not version 1: ", file_name.encode())
            return False

        self._m_shader_name = data["shader"]
        # NOTE: Skip something here until later chaps

        vert_size: int = 8

        # LOAD TEXTURES:
        textures_data: list = data["textures"]
        if not textures_data or len(textures_data) < 1:
            sdl2.SDL_Log(b"Mesh has no textures: ", file_name.encode())
            return False

        # TODO load specularPower later in chap

        for tex_name in textures_data:
            # Is texture already loaded?
            texture: Texture = renderer.get_texture(tex_name)
            if texture == None:
                # Try loading texture again
                texture = renderer.get_texture(tex_name)
                if texture == None:
                    # If still None, use default texture
                    texture = renderer.get_texture("assets/default.png")
            self._m_textures.append(texture)
            # Test
            print(len(self._m_textures))

        # LOAD VERTICES:
        verts_data: list = data["vertices"]
        if not verts_data or len(verts_data) < 1:
            sdl2.SDL_Log("Mesh has no vertices: ", file_name.encode())
            return False

        vertices: ctypes.Array = (
            ctypes.c_float * (len(verts_data) * vert_size))()
        self._m_radius = 0.0
        count: int = 0
        for vert_data in verts_data:
            # For now assume 8 elements
            if not vert_data or len(vert_data) != 8:
                sdl2.SDL_Log("Unexpected vertex format for: ",
                             file_name.encode())
                return False
            pos: Vector3D = Vector3D(vert_data[0], vert_data[1], vert_data[2])
            self._m_radius = max(self._m_radius, pos.length_sq())

            # Add floats to list
            for f in vert_data:
                vertices[count] = f
                count += 1
        count = 0

        self._m_radius = math.sqrt(self._m_radius)

        # LOAD INDICES:
        inds_data: list = data["indices"]
        if not inds_data or len(inds_data) < 1:
            sdl2.SDL_Log("Mesh has no indices: ", file_name.encode())
            return False

        indices: ctypes.Array = (
            ctypes.c_uint * (len(inds_data) * 3))()
        for ind_data in inds_data:
            if not ind_data or len(ind_data) != 3:
                sdl2.SDL_Log("Invalid indices for: ", file_name.encode())
                return False

            # Add ints to list
            for i in ind_data:
                indices[count] = i
                count += 1
        count = 0

        # Finally, create a vertex array
        self._m_vertex_array = VertexArray(vertices, int(
            len(vertices) / vert_size), indices, len(indices))
        return True

    def unload(self) -> None:
        self._m_vertex_array.delete()
        self._m_vertex_array = None

    # Get texture from specified index
    def get_texture(self, index: int) -> Texture:
        if index < len(self._m_textures):
            return self._m_textures[index]
        else:
            return None

    def get_vertex_array(self) -> VertexArray:
        return self._m_vertex_array

    def get_shader_name(self) -> str:
        return self._m_shader_name

    def get_radius(self) -> float:
        return self._m_radius

    def get_spec_power(self) -> float:
        # TODO
        pass
