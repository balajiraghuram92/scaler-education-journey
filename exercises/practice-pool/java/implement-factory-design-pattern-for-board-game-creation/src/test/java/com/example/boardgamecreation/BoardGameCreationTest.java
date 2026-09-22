package com.example.boardgamecreation;

import org.junit.jupiter.api.Test;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class BoardGameCreationTest {
    @Test
    public void testBoardGameClass() {
        String packageName = BoardGameCreationTest.class.getPackageName();

        Reflections reflections = new Reflections(packageName, new SubTypesScanner(false));
        Set<Class<? extends BoardGame>> subTypes = reflections.getSubTypesOf(BoardGame.class);

        assertEquals(3, subTypes.size(),
                "There should be 3 implementations of BoardGame class");

        boolean hasBoardGameName = Arrays.stream(BoardGame.class.getDeclaredFields())
                .anyMatch(field -> field.getType().equals(String.class));

        assertTrue(hasBoardGameName, "BoardGame class should have a String field `boardGameName`");

        boolean hasGameType = Arrays.stream(BoardGame.class.getDeclaredMethods())
                .anyMatch(method -> method.getName().equals("gameType")
                        && method.getParameterCount() == 0
                        && method.getReturnType().equals(GameType.class)
                        && Modifier.isAbstract(method.getModifiers()));
        assertTrue(hasGameType,
                "BoardGame class should have a method called gameType with no parameters and GameType return type.");

        boolean hasPlayGame = Arrays.stream(BoardGame.class.getDeclaredMethods())
                .anyMatch(method -> method.getName().equals("playGame")
                        && method.getParameterCount() == 0
                        && method.getReturnType().equals(void.class)
                        && Modifier.isAbstract(method.getModifiers()));
        assertTrue(hasPlayGame,
                "BoardGame class should have a method called playGame with no parameters and void return type.");
    }

    @Test
    public void testBoardGameFactoryClass() {
        boolean hasCreateGameMethod = Arrays.stream(BoardGameFactory.class.getDeclaredMethods())
                .anyMatch(method -> Modifier.isStatic(method.getModifiers())
                        && method.getReturnType().equals(BoardGame.class)
                        && Arrays.asList(method.getParameterTypes()).contains(GameType.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class));

        assertTrue(hasCreateGameMethod,
                "If the factory is implemented correctly, it should have a static method to create game that takes two parameters: GameType and String boardGameName.");
    }

    @Test
    public void testBoardGameFactoryMethodInvocation() {
        Method[] methods = BoardGameFactory.class.getDeclaredMethods();

        Method createGameMethod = Arrays.stream(methods)
                .filter(method -> Modifier.isStatic(method.getModifiers())
                        && method.getReturnType().equals(BoardGame.class)
                        && Arrays.asList(method.getParameterTypes()).contains(GameType.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class))
                .findFirst()
                .orElse(null);

        assertNotNull(createGameMethod , "If the factory is implemented correctly, it should have a static method to " +
                "create game that takes two parameters: GameType and String boardGameName.");

        GameType gameType = GameType.TIC_TAC_TOE;
        String boardGameName = "tictactoe";
        BoardGame boardGame = null;

        try {
            boardGame = (BoardGame) createGameMethod.invoke(null, gameType, boardGameName);
        } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
            throw new RuntimeException(e);
        }

        if (boardGame == null) {
            try {
                boardGame = (BoardGame) createGameMethod.invoke(null, boardGameName, gameType);
            } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
                throw new RuntimeException(e);
            }
        }

        assertNotNull(boardGame, "If the factory is implemented correctly, the createGame method should return a non-null Game.");
        assertEquals(GameType.TIC_TAC_TOE, boardGame.gameType(), "If the factory is implemented correctly, the create method should return a BoardGame of GameType.TIC_TAC_TOE");
        assertEquals(boardGameName, boardGame.getBoardGameName(), "If the factory is implemented correctly, the create method should return a BoardGame with name tictactoe");
    }
}
