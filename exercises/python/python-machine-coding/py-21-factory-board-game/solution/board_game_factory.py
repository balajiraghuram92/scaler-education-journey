from board_game import BoardGame
from game_type import GameType

class BoardGameFactory:
    @staticmethod
    def create_board_game(game_type: GameType, name: str) -> BoardGame:
        if game_type == GameType.TIC_TAC_TOE:
            from games.tic_tac_toe_board_game import TicTacToeBoardGame
            return TicTacToeBoardGame(name)
        elif game_type == GameType.CHESS:
            from games.chess_board_game import ChessBoardGame
            return ChessBoardGame(name)
        elif game_type == GameType.SNAKE_LADDER:
            from games.snake_ladder_board_game import SnakeLadderBoardGame
            return SnakeLadderBoardGame(name)
        else:
            raise ValueError(f"Unknown game type: {game_type}")
