from __future__ import annotations


class Renderer:
    def __init__(self) -> None:
        # Map of loaded textures
        self._m_textures = {}
        # Map of loaded meshes
        self._m_meshes = {}

        # List of sprite components
        self._m_sprite_comps = []
        # List of mesh components
        self._m_mesh_comps = []

        # Game
        self._m_game: Game

        # Sprite shader
        self._m_sprite_shader: Shader = None
        # Sprite vertex array
        self._m_sprite_verts: VertexArray = None

        # Mesh shader
        self._m_mesh_shader: Shader

        # Matrices
        self._m_view: Matrix4
        self._m_projection: Matrix4

        # Width/height of screen
        self._m_screen_width: float
        self._m_screen_height: float

        # Lighting TODO
        self._m_ambient_light: Vector3D
        self._m_dir_light: DirectionalLight

        # SDL window/context
        self._m_window: sdl2.SDL_Window = None
        self._m_context: sdl2.SDL_GLContext = None

    def _load_shaders(self) -> bool:
        pass

    def _create_sprite_verts(self) -> None:
        pass

    def _set_light_uniforms(self, shader: Shader) -> None:
        pass
