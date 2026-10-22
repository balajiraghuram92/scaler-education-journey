from dataclasses import dataclass
from enum import Enum


class GraphicType(Enum):
    JPEG = "jpeg"
    PNG = "png"
    SVG = "svg"


@dataclass
class Image:
    pass


@dataclass
class Graphic:
    """The original, un-split graphic. Leave unchanged."""

    type: GraphicType
    image: Image
    x: int
    y: int
    width: int
    height: int
    colour: str


@dataclass
class GraphicIntrinsicState:
    """Shared state, independent of where the graphic is drawn.

    Declare these fields (exact names): image, width, height, colour, type.
    """


@dataclass
class GraphicExtrinsicState:
    """Per-placement state.

    Declare these fields (exact names): x, y, and intrinsic_state, a reference to the
    shared GraphicIntrinsicState.
    """
