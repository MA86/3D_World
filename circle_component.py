from __future__ import annotations
from component import Component


class CircleComponent(Component):
    def __init__(self, owner: Actor) -> None:
        super().__init__(owner)

        self._m_radius: float = 0.0

    def intersect(self, circle_a: CircleComponent, circle_b: CircleComponent) -> bool:
        # Compute distance squared
        diff: Vector3D = circle_a.get_center() - circle_b.get_center()
        dist_sq: float = diff.length_sq()

        # Compute sum of radii squared
        radii: float = circle_a.get_radius() + circle_b.get_radius()
        radii_sq = radii * radii

        return dist_sq <= radii_sq

    def get_center(self) -> Vector3D:
        return self._m_owner.get_position()

    def get_radius(self) -> float:
        return self._m_owner.get_scale() * self._m_radius

    def set_radius(self, radius: float) -> None:
        self._m_radius = radius
