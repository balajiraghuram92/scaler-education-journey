package com.example.tttundo.strategies;

import com.example.tttundo.models.Board;
import com.example.tttundo.models.Move;

public interface WinningStrategy {
    boolean checkWinner(Board board, Move move);
}
