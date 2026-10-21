from dataclasses import dataclass
from enum import Enum


class Colour(Enum):
    WHITE = "white"
    BLACK = "black"


@dataclass
class ChessUser:
    """The original, un-split user. Leave unchanged."""

    name: str
    age: int
    gender: str
    email: str
    phone_number: str
    colour: Colour
    current_game_streak: int
    photo: bytes


@dataclass
class UserIntrinsicState:
    """Shared, per-user state that never changes between games.

    Declare these fields (exact names): name, age, gender, email, phone_number, photo.
    """


@dataclass
class UserExtrinsicState:
    """Per-game state.

    Declare these fields (exact names): colour, current_game_streak, and
    intrinsic_state, a reference to the shared UserIntrinsicState.
    """
