from board_game import BoardGame
from game_type import GameType

class SnakeLadderBoardGame(BoardGame):
    def __init__(self, board_game_name: str):
        super().__init__(board_game_name)

    def play_game(self) -> None:
        # Implement logic for playing Snake & Ladder
        print("Playing Snake & Ladder")

    def game_type(self) -> GameType:
        return GameType.SNAKE_LADDER
