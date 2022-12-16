from __future__ import annotations

import sdl2dll      # SDL DLLs
import sdl2         # SDL
import ctypes

from maths import Vector3D, Quaternion, PI_OVER_TWO, PI
from renderer import Renderer
from mesh_component import MeshComponent
from actor import State, Actor
# TODO import camera and plane


class Game:
    def __init__(self):
        # All actors
        self._m_actors = []
        self._m_pending_actors = []

        self._m_renderer: Renderer = None

        self._m_updating_actors: bool = False
        self._m_running: bool = True
        self._m_time_then: ctypes.c_uint32 = ctypes.c_uint32()

        # Game-specific code
        # TODO: add mCamera

    def initialize(self) -> bool:
        # Initialize SDL library
        result = sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_AUDIO)
        if result != 0:
            sdl2.SDL_Log(b"SDL initialization failed: ",
                         sdl2.SDL_GetError())
            return False

        # Create renderer
        self._m_renderer = Renderer(self)
        if not self._m_renderer.initialize(1024.0, 768.0):
            sdl2.SDL_Log(b"Failed to initialize renderer")
            self._m_renderer.delete()
            self._m_renderer = None
            return False

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
        if self._m_renderer:
            self._m_renderer.shutdown()
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
        for actor in self._m_actors:
            actor.input(keyb_state)

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
        self._m_renderer.draw()

    def _load_data(self) -> None:
        # Create cube actor
        a = Actor(self)
        a.set_position(Vector3D(200.0, 75.0, 0.0))
        a.set_scale(50.0)
        q = Quaternion.create_quaternion(Vector3D(0.0, 1.0, 0.0), -PI_OVER_TWO)
        q = Quaternion.concatenate(q, Quaternion.create_quaternion(
            Vector3D(0.0, 0.0, 1.0), PI + PI / 4.0))
        a.set_rotation(q)

        mc = MeshComponent(a)
        mc.set_mesh(self._m_renderer.get_mesh("assets/cube.gpmesh"))

        # TODO: create sphere actor and more...

    def _unload_data(self) -> None:
        while len(self._m_actors) != 0:
            actor = self._m_actors.pop()
            actor.delete()

        if self._m_renderer:
            self._m_renderer.unload_data()

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

    def get_renderer(self) -> Renderer:
        return self._m_renderer
