from __future__ import annotations
from component import Component
from maths import Vector3D, check_near_zero, Quaternion


class MoveComponent(Component):
    def __init__(self, owner: Actor, update_order: int = 10) -> None:
        super().__init__(owner, update_order)

        # For simple rotation (rad/sec)
        self._m_rotation_speed: float = 0.0

        # For Newtonian movement
        self._m_mass: float = 1.0
        self._m_sum_forces: Vector3D = Vector3D(0.0, 0.0, 0.0)
        self._m_velocity: Vector3D = Vector3D(0.0, 0.0, 0.0)

    # Implements
    def update(self, dt: float) -> None:
        if not check_near_zero(self._m_rotation_speed):
            # Simple rotation
            rot: Quaternion = self._m_owner.get_rotation()
            angle: float = self._m_rotation_speed * dt
            # Create a quaternion for incremental rotation (about up axis)
            rot_new = Quaternion.create_quaternion(
                Vector3D(0.0, 0.0, 1.0), angle)
            # Concatenate new and old rotations
            rot = Quaternion.concatenate(rot, rot_new)
            self._m_owner.set_rotation(rot)

        ## Velocity Verlet Integration: start ##
        pos: Vector3D = self._m_owner.get_position()
        # Compute acceleration (F = m * a)
        acceleration: Vector3D = self._m_sum_forces * (1 / self._m_mass)
        # Then reset every frame
        self._m_sum_forces.set(0.0, 0.0, 0.0)
        # Compute delta-v & delta-p (dv=a*dt, dp=v/2*dt)
        old_velocity: Vector3D = self._m_velocity
        self._m_velocity = self._m_velocity + acceleration * dt
        pos = pos + (old_velocity + self._m_velocity) * 0.5 * dt
        ## Velocity Verlet Integration: end ##

        """
        # Screen wrapping (for Asteroid only, remove for generic MoveComponent)
        if pos.x < -550.0:
            pos.x = 550.0
        elif pos.x > 550.0:
            pos.x = -550.0
        if pos.y < -450.0:
            pos.y = 450.0
        elif pos.y > 450.0:
            pos.y = -450.0
        """

        self._m_owner.set_position(pos)

    def add_force(self, force: Vector3D) -> None:
        self._m_sum_forces = self._m_sum_forces + force

    def get_rotation_speed(self) -> float:
        return self._m_rotation_speed

    def set_rotation_speed(self, speed: float) -> None:
        self._m_rotation_speed = speed

    def get_mass(self) -> None:
        return self._m_mass

    def set_mass(self, mass: float) -> None:
        self._m_mass = mass
