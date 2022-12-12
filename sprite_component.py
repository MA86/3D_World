from __future__ import annotations
import sdl2
import OpenGL.GL as GL
from maths import Matrix4
import ctypes
from component import Component
from shader import Shader


class SpriteComponent(Component):
    def __init__(self, owner: Actor, draw_order: int = 100) -> None:
        super().__init__(owner)
        self.m_texture: Texture = None
        self.m_draw_order: int = draw_order
        self.m_text_width: int = 0
        self.m_text_height: int = 0

        self._m_owner.get_game().add_sprite(self)

    def delete(self) -> None:
        # Remove from owner's list
        super().delete()
        # Remove from game's list
        self._m_owner.get_game().remove_sprite(self)

    def draw(self, shader: Shader) -> None:
        # Scale quad mesh by width/height of texture
        scale_mat: Matrix4 = Matrix4.create_scale_matrix_xyz(
            float(self.m_text_width),
            float(self.m_text_height),
            1.0)
        # Calculate world transform matrix
        world_mat: Matrix4 = scale_mat * self._m_owner.get_world_transform()

        # Note: since sprites use the same shader/mesh,
        # the game first sets them active before sprite draws

        # Set world transform matrix in shader
        shader.set_matrix_uniform("uWorldTransform", world_mat)

        # Set current texture [can set diff. texture for each draw!]
        self.m_texture.set_active()

        # Draw quad mesh
        GL.glDrawElements(
            GL.GL_TRIANGLES,    # Type of shape to draw
            6,                  # Indices in index buffer
            GL.GL_UNSIGNED_INT,  # Type of index
            None
        )

    def set_texture(self, texture: Texture) -> None:
        self.m_texture = texture

        # Set width/height
        self.m_text_width = texture.get_width()
        self.m_text_height = texture.get_height()

    def get_draw_order(self) -> int:
        return self.m_draw_order

    def get_text_height(self) -> int:
        return self.m_text_height

    def get_text_width(self) -> int:
        return self.m_text_width
