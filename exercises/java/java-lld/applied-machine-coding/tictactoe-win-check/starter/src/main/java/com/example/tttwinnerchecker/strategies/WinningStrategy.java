package com.example.tttwinnerchecker.strategies;

import com.example.tttwinnerchecker.models.Board;
import com.example.tttwinnerchecker.models.Move;

public interface WinningStrategy {
    boolean checkWinner(Board board, Move move);
}
