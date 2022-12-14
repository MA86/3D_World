from __future__ import annotations
import OpenGL.GL as GL
from component import Component


class MeshComponent(Component):
    def __init__(self, owner: Actor) -> None:
        super().__init__(owner)

        self._m_mesh: Mesh = None
        self._m_texture_index: int = 0

        self._m_owner.get_game().get_renderer().add_mesh_comp(self)

    # TODO see who calls this
    def delete(self) -> None:
        # Remove from owner's list
        super().delete()
        # Remove from Game's list
        self._m_owner.get_game().get_renderer().remove_mesh_comp(self)

    # Implementable
    def draw(self, shader: Shader) -> None:
        if self._m_mesh:
            # Set world transform uniform
            shader.set_matrix_uniform(
                "uWorldTransform", self._m_owner.get_world_transform())
            # TODO: later set specular power
            # Set the active texture
            texture: Texture = self._m_mesh.get_texture(self._m_texture_index)
            if texture:
                texture.set_active()
            # Set the mesh's vertex array as active
            vert_arr: VertexArray = self._m_mesh.get_vertex_array()
            vert_arr.set_active()
            # Draw
            GL.glDrawElements(
                GL.GL_TRIANGLES, vert_arr.get_num_indices(), GL.GL_UNSIGNED_INT, None)

    # Implementable
    def set_mesh(self, mesh: Mesh) -> None:
        self._m_mesh = mesh

    def set_texture_index(self, index: int) -> None:
        self._m_texture_index = index
