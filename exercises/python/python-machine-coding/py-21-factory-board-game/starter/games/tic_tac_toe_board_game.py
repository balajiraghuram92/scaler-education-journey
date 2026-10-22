from board_game import BoardGame
from game_type import GameType

class TicTacToeBoardGame(BoardGame):
    def __init__(self, board_game_name: str):
        super().__init__(board_game_name)

    def play_game(self) -> None:
        # Implement logic for playing Tic Tac Toe
        print("Playing Tic Tac Toe")

    def game_type(self) -> GameType:
        return GameType.TIC_TAC_TOE
