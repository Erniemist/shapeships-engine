from enum import Enum, auto
from typing import Self


class Phase(Enum):
    BUILD = auto()
    BATTLE = auto()

    def next_phase(self) -> Self:
        return {
            self.BUILD: Phase.BATTLE,
            self.BATTLE: Phase.BUILD,
        }[self]
