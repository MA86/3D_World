from __future__ import annotations
import sdl2
from maths import Vector3D, Matrix4, TWO_PI
from actor import Actor
from move_component import MoveComponent


class CameraActor(Actor):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self._m_move_comp = MoveComponent(self)

    # Implements
    def update_actor(self, dt: float) -> None:
        # Dead code? TODO
        super().update_actor(dt)

        # Compute new camera from this actor
        camera_pos: Vector3D = self.get_position()
        target: Vector3D = self.get_position() + self.get_forward() * 100.0
        up: Vector3D = Vector3D(0.0, 0.0, 1.0)

        view: Matrix4 = Matrix4.create_look_at(camera_pos, target, up)
        self.get_game().get_renderer().set_view_matrix(view)

    # Implements
    def input_actor(self, keyb_state: ctypes.Array) -> None:
        # Dead code? TODO
        super().input_actor(keyb_state)

        # TODO forward
        rotation_speed: float = 0.0

        if keyb_state[sdl2.SDL_SCANCODE_A]:
            rotation_speed -= TWO_PI
        if keyb_state[sdl2.SDL_SCANCODE_D]:
            rotation_speed += TWO_PI

        self._m_move_comp.set_rotation_speed(rotation_speed)
