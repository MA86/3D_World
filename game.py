from __future__ import annotations

import sdl2dll      # SDL DLLs
import sdl2         # SDL
import sdl2.sdlimage as sdlimage    # SDL Image
import OpenGL.GL as GL

from vertex_array import VertexArray
from shader import Shader
from randoms import Random
from maths import Vector2D, Matrix4
from texture import Texture
import maths
import ctypes

from ship import Ship
from actor import State
from asteroid import Asteroid


class Game:
    def __init__(self):
        # For SDL use
        self._m_window: sdl2.SDL_Window = None
        self._m_context: sdl2.SDL_GLContext = None
        self._m_renderer = None  # TODO

        # All loaded textures
        self._m_textures = {}

        # All actors
        self._m_actors = []
        self._m_pending_actors = []

        # All sprites drawn
        self._m_sprites = []

        # Sprite shader
        self._m_sprite_shader: Shader = None
        # Sprite mesh (represented by vertex array)
        self._m_sprite_vertices: VertexArray = None

        self._m_updating_actors: bool = False
        self._m_running: bool = True
        self._m_time_then: ctypes.c_uint32 = ctypes.c_uint32()

        # Game-specific objects (refs and lists)
        self._m_ship: Ship = None
        self._m_asteroids = []

    def initialize(self) -> bool:
        # Initialize SDL library
        result = sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_AUDIO)
        if result != 0:
            sdl2.SDL_Log(b"SDL initialization failed: ",
                         sdl2.SDL_GetError())
            return False

        # First, configure attributes for OpenGL: start
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_PROFILE_MASK,
                                 sdl2.SDL_GL_CONTEXT_PROFILE_CORE)  # Set core profile
        # Set version 3.3
        sdl2.SDL_GL_SetAttribute(
            sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 3)
        # Set color buffer
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_RED_SIZE,
                                 8)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_GREEN_SIZE, 8)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_BLUE_SIZE, 8)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_ALPHA_SIZE, 8)
        # Enable double buffer
        sdl2.SDL_GL_SetAttribute(
            sdl2.SDL_GL_DOUBLEBUFFER, 1)
        # Enable hardware acceleration
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_ACCELERATED_VISUAL, 1)
        # First, configure attributes for OpenGL: end

        # Second, create window for OpenGL
        self._m_window = sdl2.SDL_CreateWindow(b"Spaceship Shooter 3D",
                                               sdl2.SDL_WINDOWPOS_CENTERED,
                                               sdl2.SDL_WINDOWPOS_CENTERED, 1024, 768, sdl2.SDL_WINDOW_OPENGL)
        if self._m_window == None:
            sdl2.SDL_Log(b"Window failed: ", sdl2.SDL_GetError())
            return False

        # Third, create context for OpenGL (Contains color buff., textures, models, etc.)
        self._m_context = sdl2.SDL_GL_CreateContext(self._m_window)

        # Fourth, load shaders
        if not self._load_shaders():
            sdl2.SDL_Log(b"Failed to load shader program")
            return False

        # Fifth, create quad mesh for drawing
        self._create_sprite_vertices()

        # Initialize SDL image library
        if sdlimage.IMG_Init(sdlimage.IMG_INIT_PNG) == 0:
            sdl2.SDL_Log(b"Image initialization failed: ", sdl2.SDL_GetError())
            return False

        # Initiate random generator class
        Random.init(4)

        self._load_data()

        # Initial time
        self._m_time_then = sdl2.SDL_GetTicks()

        return True

    def run_loop(self) -> None:
        while self._m_running:
            self._process_input()
            self._process_update()
            self._process_output()

    def shutdown(self) -> None:
        # Shutdown in reverse
        self._unload_data()
        self._m_sprite_vertices.delete()
        self._m_sprite_shader.unload()
        del self._m_sprite_shader
        sdlimage.IMG_Quit()
        sdl2.SDL_GL_DeleteContext(self._m_context)
        sdl2.SDL_DestroyWindow(self._m_window)
        sdl2.SDL_Quit()

    def _process_input(self) -> None:
        event = sdl2.SDL_Event()    # Empty object
        # Get and check events-queue
        while sdl2.SDL_PollEvent(event):
            if event.type == sdl2.SDL_QUIT:
                self._m_running = False

        # Get states-queue
        keyb_state = sdl2.SDL_GetKeyboardState(None)

        # Check states-queue for Game
        if keyb_state[sdl2.SDL_SCANCODE_ESCAPE]:
            self._m_running = False
        # Check states-queue for Actors
        self._m_updating_actors = True
        for actor in self._m_actors:
            actor.input(keyb_state)
        self._m_updating_actors = False

    def _process_update(self) -> None:
        # Wait 16ms (frame limiting)
        sdl2.SDL_Delay(16)

        time_now: ctypes.c_uint32 = sdl2.SDL_GetTicks()
        delta_time: float = (time_now - self._m_time_then) / 1000.0
        # Clamp max delta time (for debugging)
        if delta_time > 0.05:
            delta_time = 0.05
        # Time now is time then
        self._m_time_then: ctypes.c_uint32 = sdl2.SDL_GetTicks()

        # Update actors
        self._m_updating_actors = True
        for actor in self._m_actors:
            actor.update(delta_time)
        self._m_updating_actors = False

        # Add pending actors
        for pending_actor in self._m_pending_actors:
            pending_actor.compute_world_transform()
            self._m_actors.append(pending_actor)
        self._m_pending_actors.clear()

        # Collect dead actors
        dead_actors = []
        for dead_actor in self._m_actors:
            if dead_actor.get_state() == State.eDEAD:
                dead_actors.append(dead_actor)

        # Remove dead actors from self._m_actors
        for da in dead_actors:
            da.delete()

    def _process_output(self) -> None:
        # Clear color-buffer to gray
        GL.glClearColor(0.86, 0.86, 0.86, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Enable alpha blending on color buffer
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(
            GL.GL_SRC_ALPHA,
            GL.GL_ONE_MINUS_SRC_ALPHA)

        # First, set shader and vertex array active 'every frame'
        self._m_sprite_shader.set_active()
        self._m_sprite_vertices.set_active()

        # Second, draw sprites
        for sprite in self._m_sprites:
            sprite.draw(self._m_sprite_shader)

        # Swap color-buffer to display on screen
        sdl2.SDL_GL_SwapWindow(self._m_window)

        return True

    def _load_shaders(self) -> bool:
        self._m_sprite_shader = Shader()
        if not self._m_sprite_shader.load("shaders/sprite.vert", "shaders/sprite.frag"):
            return False
        self._m_sprite_shader.set_active()

        # Set the view-projection matrix
        view_proj: Matrix4 = Matrix4.create_simple_view_proj(1024.0, 768.0)
        self._m_sprite_shader.set_matrix_uniform("uViewProj", view_proj)

        return True

    def _create_sprite_vertices(self) -> None:
        vertices: ctypes.Array = (ctypes.c_float * 20)(
            -0.5, 0.5, 0.0, 0.0, 0.0,    # Top left
            0.5, 0.5, 0.0, 1.0, 0.0,     # Top right
            0.5, -0.5, 0.0, 1.0, 1.0,    # Bottom right
            -0.5, -0.5, 0.0, 0.0, 1.0    # Bottom left
        )

        indices: ctypes.Array = (ctypes.c_uint * 6)(
            0, 1, 2,
            2, 3, 0
        )

        # Vertices describing a quad (AKA quad mesh used for all sprites!)
        self._m_sprite_vertices = VertexArray(
            vertices, 4, indices, 6)

    def _load_data(self) -> None:
        # Ship and its components (composed in constructor)
        self._m_ship = Ship(self)
        self._m_ship.set_rotation(maths.PI_OVER_TWO)
        # TODO uncomment asteroids

        # Asteroids and its components (composed in constructor)
        num_asteroids = range(1, 21)
        for i in num_asteroids:
            Asteroid(self)

    def _unload_data(self) -> None:
        while len(self._m_actors) != 0:
            actor = self._m_actors.pop()
            actor.delete()
        for texture in self._m_textures.values():
            texture.unload()
            texture.delete()
        self._m_textures.clear()

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

    def add_actor(self, actor: Actor) -> None:
        if self._m_updating_actors:
            self._m_pending_actors.append(actor)
        else:
            self._m_actors.append(actor)

    def remove_actor(self, actor: Actor) -> None:
        # Check in pending-actors list
        if actor in self._m_pending_actors:
            self._m_pending_actors.remove(actor)
        # Check in actors list
        if actor in self._m_actors:
            self._m_actors.remove(actor)

    def add_sprite(self, sprite: SpriteComponent) -> None:
        # Add based on draw order
        index = 0
        for i, c in enumerate(self._m_sprites):
            index = i
            if sprite.get_draw_order() < c.get_draw_order():
                break
        self._m_sprites.insert(index, sprite)

    def remove_sprite(self, sprite: SpriteComponent) -> None:
        self._m_sprites.remove(sprite)

    # Game-specific (add/remove asteroid)
    def add_asteroid(self, asteroid: Asteroid) -> None:
        self._m_asteroids.append(asteroid)

    def remove_asteroid(self, asteroid: Asteroid) -> None:
        self._m_asteroids.remove(asteroid)

    def get_asteroids(self) -> List[Asteroid]:
        return self._m_asteroids
