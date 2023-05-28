from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.gazo import Replay2Picture

from . import vector


class CanvasStyle(Enum):
    default = 1
    akatsuki = 2


@dataclass
class CanvasSettings:
    resolution: vector.Vector2 = field(default_factory=vector.Vector2(x=1920, y=1080))  # type: ignore
    style: CanvasStyle = field(default=CanvasStyle.default)
    context: "Replay2Picture" = field(default=None)  # type: ignore

    #
    background_blur: float = field(default=5)
    background_dim: float = field(default=0.4)
    background_border: float = field(default=32)

    #
    message: str = field(default="")

    @property
    def scale(self) -> float:
        return self.resolution.y / 720.0
