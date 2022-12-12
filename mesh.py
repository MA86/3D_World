from __future__ import annotations


class Mesh:
    """
    Encapsulates mesh loading.
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
        raise NotImplementedError()

    def get_vertex_array(self) -> VertexArray:
        return self._m_vertex_array

    # Get texture from specified index
    def get_texture(self, index: int) -> Texture:
        pass

    def get_shader_name(self) -> str:
        return self._m_shader_name

    def get_radius(self) -> float:
        return self._m_radius

    def get_spec_power(self) -> float:
        # TODO
        pass
