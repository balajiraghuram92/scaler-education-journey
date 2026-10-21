from typing import List
from exceptions.exceptions import EmptyMovesException, GameInvalidationException, InvalidMoveException
from models.enums import CellState, GameState
from models.game import Game
from models.move import Move
from models.player import Player
from strategies.winning_strategy import WinningStrategy

class GameService:

    def __init__(self, winning_strategy: WinningStrategy):
        self.winning_strategy = winning_strategy

    def start_game(self, dimension: int, players: List[Player]) -> Game:
        if dimension < 3:
            raise GameInvalidationException('Dimension must be at least 3')
        return Game(dimension, players)

    def validate_move(self, game: Game, row: int, col: int) -> bool:
        if row < 0 or row >= game.board.dimension or col < 0 or (col >= game.board.dimension):
            return False
        if game.board.board[row][col].cell_state != CellState.EMPTY:
            return False
        return True

    def make_move(self, game: Game, row: int, col: int) -> None:
        current_player = game.players[game.next_player_move_index]
        if not self.validate_move(game, row, col):
            raise InvalidMoveException(f'Invalid move made by player: {current_player.name}')
        cell_to_update = game.board.board[row][col]
        cell_to_update.cell_state = CellState.FILLED
        cell_to_update.player = current_player
        final_move = Move(current_player, cell_to_update)
        game.moves.append(final_move)
        game.next_player_move_index += 1
        game.next_player_move_index %= len(game.players)
        if self.winning_strategy.check_winner(game.board, final_move):
            game.game_state = GameState.ENDED
            game.winner = current_player
        elif len(game.moves) == game.board.dimension * game.board.dimension:
            game.game_state = GameState.DRAW

    def undo(self, game: Game) -> None:
        """Raise EmptyMovesException if game.moves is empty. Otherwise pop the last move, reset its cell (EMPTY, no player), step next_player_move_index back by one (wrapping), call winning_strategy.handle_undo(board, move), and if the game was ENDED or DRAW return it to IN_PROGRESS with winner None."""
        raise NotImplementedError('TODO: implement undo')
