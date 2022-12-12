from __future__ import annotations
import ctypes


class Component:
    """ COMPONENT BASE CLASS """

    def __init__(self, owner: Actor, update_order: int = 100) -> None:
        self._m_owner: Actor = owner
        self._m_update_order: int = update_order

        # Add self to owner's component list
        owner.add_component(self)

    def delete(self) -> None:
        self._m_owner.remove_component(self)

    def update(self, dt: float) -> None:
        # Implementable
        pass

    def input(self, keyb_state: ctypes.Array) -> None:
        # Implementable
        pass

    # Called when owner's world transform changes
    def on_update_world_transform(self) -> None:
        # Implementable
        pass

    def get_update_order(self) -> int:
        return self._m_update_order
