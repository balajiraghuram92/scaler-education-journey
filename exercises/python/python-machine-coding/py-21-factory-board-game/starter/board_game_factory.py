from board_game import BoardGame
from game_type import GameType

class BoardGameFactory:

    @staticmethod
    def create_board_game(game_type: GameType, name: str) -> BoardGame:
        """Return TicTacToeBoardGame, ChessBoardGame or SnakeLadderBoardGame (from games/) for the given GameType, constructed with name. Raise ValueError for anything else."""
        raise NotImplementedError('TODO: implement create_board_game')
