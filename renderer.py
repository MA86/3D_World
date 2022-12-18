from __future__ import annotations
import sdl2dll      # SDL DLLs
import sdl2         # SDL
import sdl2.sdlimage as sdlimage    # SDL Image
import OpenGL.GL as GL

from vertex_array import VertexArray
from shader import Shader
from maths import Matrix4, Vector3D, to_radians
from texture import Texture
from mesh import Mesh
import ctypes

# TODO later, add struct for directional light


class Renderer:
    def __init__(self, game: Game) -> None:
        # Map of loaded textures
        self._m_textures = {}
        # Map of loaded meshes
        self._m_meshes = {}

        # List of sprite components
        self._m_sprite_comps = []
        # List of mesh components
        self._m_mesh_comps = []

        # Game
        self._m_game: Game = game

        # Sprite shader
        self._m_sprite_shader: Shader = None
        # Sprite vertex array
        self._m_sprite_verts: VertexArray = None

        # Mesh shader
        self._m_mesh_shader: Shader = None

        # Matrices
        self._m_view: Matrix4 = None
        self._m_projection: Matrix4 = None

        # Width/height of screen
        self._m_screen_width: float = None
        self._m_screen_height: float = None

        # Lighting TODO
        self._m_ambient_light: Vector3D = None
        self._m_dir_light: DirectionalLight = None

        # SDL window/context
        self._m_window: sdl2.SDL_Window = None
        self._m_context: sdl2.SDL_GLContext = None

    def delete(self) -> None:
        # Does nothing yet
        pass

    def initialize(self, screen_width: float, screen_height: float) -> bool:
        self._m_screen_width = screen_width
        self._m_screen_height = screen_height

        # First, set OpenGL properties: start...
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_PROFILE_MASK,
                                 sdl2.SDL_GL_CONTEXT_PROFILE_CORE)  # Set core profile
        # Set version 3.3
        sdl2.SDL_GL_SetAttribute(
            sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 3)
        # Set color buffer
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_RED_SIZE, 8)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_GREEN_SIZE, 8)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_BLUE_SIZE, 8)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_ALPHA_SIZE, 8)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_DEPTH_SIZE, 24)
        # Enable double buffer
        sdl2.SDL_GL_SetAttribute(
            sdl2.SDL_GL_DOUBLEBUFFER, 1)
        # Enable hardware acceleration
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_ACCELERATED_VISUAL, 1)
        # First, set OpenGL properties: end...

        # Second, create window for OpenGL
        self._m_window = sdl2.SDL_CreateWindow(b"3D Prototype",
                                               sdl2.SDL_WINDOWPOS_CENTERED,
                                               sdl2.SDL_WINDOWPOS_CENTERED,
                                               int(self._m_screen_width),
                                               int(self._m_screen_height),
                                               sdl2.SDL_WINDOW_OPENGL)
        if self._m_window == None:
            sdl2.SDL_Log(b"Window failed: ", sdl2.SDL_GetError())
            return False

        # Third, create context for OpenGL (Contains color buff., textures, models, etc.)
        self._m_context = sdl2.SDL_GL_CreateContext(self._m_window)

        # Initialize SDL image library
        if sdlimage.IMG_Init(sdlimage.IMG_INIT_PNG) == 0:
            sdl2.SDL_Log(b"Image initialization failed: ", sdl2.SDL_GetError())
            return False

        # Fourth, load shaders
        if not self._load_shaders():
            sdl2.SDL_Log(b"Failed to load shader program")
            return False

        # Fifth, create quad mesh for sprites
        self._create_sprite_vertices()

        return True

    def shutdown(self) -> None:
        # Shutdown in reverse
        self._m_sprite_vertices.delete()
        self._m_sprite_shader.unload()
        del self._m_sprite_shader
        self._m_mesh_shader.unload()
        self._m_mesh_shader.delete()
        sdlimage.IMG_Quit()
        sdl2.SDL_GL_DeleteContext(self._m_context)
        sdl2.SDL_DestroyWindow(self._m_window)

    def unload_data(self) -> None:
        # Destroy textures
        for texture in self._m_textures.values():
            texture.unload()
            texture.delete()
        self._m_textures.clear()
        # Destroy meshes
        for mesh in self._m_meshes.values():
            mesh.unload()
            mesh.delete()
        self._m_meshes.clear()

    def draw(self) -> None:
        # Clear color-buffer to gray
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # DRAW MESH COMPONENTS: Start...
        # Enable depth buffering and disable alpha blending
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_BLEND)

        # Set mesh shader active
        self._m_mesh_shader.set_active()
        # Update view-proj matrix uniform
        self._m_mesh_shader.set_matrix_uniform(
            "uViewProj", self._m_view * self._m_projection)

        # TODO Update lighting uniforms

        for mesh_comp in self._m_mesh_comps:
            # [Note: mesh vertex array is set active in this draw!]
            mesh_comp.draw(self._m_mesh_shader)
        # DRAW MESH COMPONENTS: End...

        # DRAW ALL SPRITE COMPONENTS: Start...
        # Disable depth buffering
        GL.glDisable(GL.GL_DEPTH_TEST)
        # Enable alpha blending on color buffer
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendEquationSeparate(GL.GL_FUNC_ADD, GL.GL_FUNC_ADD)
        GL.glBlendFuncSeparate(
            GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA, GL.GL_ONE, GL.GL_ZERO)

        # Set shader and vertex array active 'every frame'
        self._m_sprite_shader.set_active()
        self._m_sprite_vertices.set_active()

        # Draw sprites
        for sprite in self._m_sprite_comps:
            sprite.draw(self._m_sprite_shader)

        # Swap color-buffer to display on screen
        sdl2.SDL_GL_SwapWindow(self._m_window)
        # DRAW ALL SPRITE COMPONENTS: End...

    def add_sprite(self, sprite: SpriteComponent) -> None:
        # Add based on draw order
        index = 0
        for i, c in enumerate(self._m_sprite_comps):
            index = i
            if sprite.get_draw_order() < c.get_draw_order():
                break
        self._m_sprite_comps.insert(index, sprite)

    def remove_sprite(self, sprite: SpriteComponent) -> None:
        self._m_sprite_comps.remove(sprite)

    def add_mesh_comp(self, mesh: MeshComponent) -> None:
        self._m_mesh_comps.append(mesh)

    def remove_mesh_comp(self, mesh: MeshComponent) -> None:
        self._m_mesh_comps.remove(mesh)

    def get_texture(self, file_name: str) -> Texture:
        # Search for texture in dic first
        texture: Texture = self._m_textures.get(file_name)
        if texture != None:
            return texture
        else:
            texture = Texture()
            if texture.load(file_name):
                # Add texture to dic
                self._m_textures[file_name] = texture
            else:
                texture.delete()
                texture = None
        return texture

    def get_mesh(self, file_name: str) -> Mesh:
        # Search for mesh in dic first
        mesh: Mesh = self._m_meshes.get(file_name)
        if mesh != None:
            return mesh
        else:
            mesh = Mesh()
            if mesh.load(file_name, self):
                # Add mesh to dic
                self._m_meshes[file_name] = mesh
            else:
                mesh.delete()
                mesh = None
        return mesh

    def _load_shaders(self) -> bool:
        # Create sprite shader
        self._m_sprite_shader = Shader()
        if not self._m_sprite_shader.load("shaders/sprite.vert", "shaders/sprite.frag"):
            return False
        self._m_sprite_shader.set_active()

        # Set the view-projection matrix for uniform
        view_proj: Matrix4 = Matrix4.create_simple_view_proj(
            self._m_screen_width, self._m_screen_height)
        self._m_sprite_shader.set_matrix_uniform("uViewProj", view_proj)

        # Create mesh shader
        self._m_mesh_shader = Shader()
        if not self._m_mesh_shader.load("shaders/basic_mesh.vert", "shaders/basic_mesh.frag"):
            return False
        self._m_mesh_shader.set_active()

        # Set the view-projection matrix for uniform
        self._m_view: Matrix4 = Matrix4.create_look_at(
            Vector3D(0.0, 0.0, 0.0),    # Camera position
            Vector3D(1.0, 0.0, 0.0),    # Target position
            Vector3D(0.0, 0.0, 1.0))    # Up
        self._m_projection: Matrix4 = Matrix4.create_perspective_FOV(
            to_radians(70.0),   # Horizontal FOV
            self._m_screen_width,   # Width of view
            self._m_screen_height,  # Height of view
            25.0,                   # Near plane distance
            10000.0)                # Far plane distance
        self._m_mesh_shader.set_matrix_uniform(
            "uViewProj", self._m_view * self._m_projection)

        return True

    def _create_sprite_vertices(self) -> None:
        vertices: ctypes.Array = (ctypes.c_float * 32)(
            -0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,   # Top left
            0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0,    # Top right
            0.5, -0.5, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0,   # Bottom right
            -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0   # Bottom left
        )

        indices: ctypes.Array = (ctypes.c_uint * 6)(
            0, 1, 2,
            2, 3, 0
        )

        # Vertices describing a quad (AKA quad mesh used for all sprites!)
        self._m_sprite_vertices = VertexArray(
            vertices, 4, indices, 6)

    def _set_light_uniforms(self, shader: Shader) -> None:
        # TODO later chap
        pass

    def set_view_matrix(self, view: Matrix4) -> None:
        self._m_view = view

    def set_ambient_light(self, ambient: Vector3D) -> None:
        self._m_ambient_light = ambient

    def get_directional_light(self) -> DirectionalLight:
        return self._m_dir_light

    def get_screen_width(self) -> float:
        return self._m_screen_width

    def get_screen_height(self) -> float:
        return self._m_screen_height
