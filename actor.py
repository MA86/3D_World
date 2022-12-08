from __future__ import annotations
from typing import List         # For hinting
from enum import Enum           # For enum
import ctypes
from maths import Vector3D, Matrix4, Quaternion
import maths


class State(Enum):
    eALIVE = 1
    ePAUSED = 2
    eDEAD = 3


class Actor:
    """ ACTOR BASE CLASS """

    def __init__(self, game: Game) -> None:
        # State
        self._m_state: State = State.eALIVE

        # Transform: start
        # Matrix4 because layout assumes vertices have a z component (x,y,z,w)
        self._m_world_transform: Matrix4 = None
        self._m_recompute_world_transform: bool = True
        self._m_position: Vector3D = Vector3D(0.0, 0.0, 0.0)
        self._m_scale: float = 1.0
        self._m_rotation: Quaternion = Quaternion()
        # Transform: end

        # Components (sorted)
        self._m_components: List[Component] = []

        # Loose association
        self._m_game: Game = game

        # Add self to list
        game.add_actor(self)

    def delete(self) -> None:
        # If container gone -> contained gone! [Composition]
        self._m_game.remove_actor(self)
        for c in list(self._m_components):
            c.delete()

    def update(self, dt: float) -> None:
        if self._m_state == State.eALIVE:
            self.compute_world_transform()

            self.update_components(dt)
            self.update_actor(dt)

            self.compute_world_transform()

    def update_components(self, dt: float) -> None:
        for c in self._m_components:
            c.update(dt)

    def update_actor(self, dt: float) -> None:
        # Implementable
        pass

    def input(self, keyb_state: ctypes.Array) -> None:
        if self._m_state == State.eALIVE:
            self.input_components(keyb_state)
            self.input_actor(keyb_state)

    def input_components(self, keyb_state: ctypes.Array) -> None:
        for c in self._m_components:
            c.input(keyb_state)

    def input_actor(self, keyb_state: ctypes.Array) -> None:
        # Implementable
        pass

    def compute_world_transform(self) -> None:
        if self._m_recompute_world_transform:
            self._m_recompute_world_transform = False

            # Calculate transformation matrices
            temp_scale = Matrix4.create_scale_matrix_uniform(self._m_scale)
            temp_rotation = Matrix4.create_from_quaternion(self._m_rotation)
            temp_translation = Matrix4.create_translation_matrix(
                Vector3D(self._m_position.x, self._m_position.y, self._m_position.z))

            # Multiply in order
            self._m_world_transform = temp_scale * temp_rotation * temp_translation

            # Inform components that world transform updated
            for comp in self._m_components:
                comp.on_update_world_transform()

    def add_component(self, component: Component) -> None:
        # Add based on update order
        index = 0
        for i, c in enumerate(self._m_components):
            index = i
            if component.get_update_order() < c.get_update_order():
                break
        self._m_components.insert(index, component)

    def remove_component(self, component: Component) -> None:
        self._m_components.remove(component)

    # Getters/setters
    def get_position(self) -> Vector3D:
        return self._m_position

    def set_position(self, pos: Vector3D) -> None:
        self._m_position = pos
        self._m_recompute_world_transform = True

    def get_scale(self) -> float:
        return self._m_scale

    def set_scale(self, scale: float) -> None:
        self._m_scale = scale
        self._m_recompute_world_transform = True

    def get_rotation(self) -> Quaternion:
        return self._m_rotation

    def set_rotation(self, rotation: Quaternion) -> None:
        self._m_rotation = rotation
        self._m_recompute_world_transform = True

    def get_world_transform(self) -> Matrix4:
        return self._m_world_transform

    def get_forward(self) -> Vector3D:
        # Initial forward vector is: +x -> (1, 0, 0)
        return Vector3D.transform_q(Vector3D(1.0, 0.0, 0.0), self._m_rotation)

    def get_state(self) -> State:
        return self._m_state

    def set_state(self, state: State) -> None:
        self._m_state = state

    def get_game(self) -> Game:
        return self._m_game
