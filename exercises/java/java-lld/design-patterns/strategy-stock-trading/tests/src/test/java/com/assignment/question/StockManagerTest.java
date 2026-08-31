package com.assignment.question;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
public class StockManagerTest {

    private static Constructor<?> getStrategyConstructor() {
        Class<?> pricingManagerClass = StockTradingManager.class;
        Constructor<?>[] constructors = pricingManagerClass.getDeclaredConstructors();

        Predicate<Constructor<?>> singleField = constructor -> constructor.getParameterCount() == 1 && constructor.getParameterTypes()[0] == TradingIndicatorStrategy.class;
        Predicate<Constructor<?>> twoFields = constructor -> constructor.getParameterCount() == 2 && constructor.getParameterTypes()[0] == TradingStrategyType.class && constructor.getParameterTypes()[1] == TradingIndicatorStrategy.class;
        return Stream.of(constructors).filter(constructor -> singleField.or(twoFields).test(constructor)).findFirst().orElse(null);
    }

    @Test
    public void testConcreteStrategies() {
        Reflections reflections = new Reflections(StockManagerTest.class.getPackageName(), new SubTypesScanner(false));
        Set<Class<? extends TradingIndicatorStrategy>> subTypes = reflections.getSubTypesOf(TradingIndicatorStrategy.class);

        assertEquals(3, subTypes.size(), "If the strategy pattern is implemented correctly, there should be 3 concrete strategies for each pricing type.");
    }

    @Test
    public void testCalculateIndicatorStrategyMethod() {

        Class<?> strategyClass = TradingIndicatorStrategy.class;
        Method[] methods = strategyClass.getDeclaredMethods();

        boolean hasCalculateIndicatorMethod = Stream.of(methods).anyMatch(method -> method.getParameterCount() == 1 && method.getParameterTypes()[0] == Stock.class && method.getReturnType() == Double.class);
        assertTrue(hasCalculateIndicatorMethod, "If the strategy pattern is implemented correctly, TradingIndicatorStrategy should have a method that accepts a Stock object and returns a Double.");
    }

    @Test
    public void testPricingManagerFields() {
        Class<?> pricingManagerClass = StockTradingManager.class;
        Field[] fields = pricingManagerClass.getDeclaredFields();

        boolean hasStrategyField = Stream.of(fields).anyMatch(field -> Modifier.isPrivate(field.getModifiers()) && field.getType() == TradingIndicatorStrategy.class);

        assertTrue(hasStrategyField, "If the strategy pattern is implemented correctly, StockTradingManager should have a private field of type TradingIndicatorStrategy.");
    }

    @Test
    public void testPricingManagerConstructor() {
        assertNotNull(getStrategyConstructor(), "If the strategy pattern is implemented correctly, StockTradingManager should have a constructor that accepts a TradingIndicatorStrategy object.");
    }

    @Test
    public void testPricingStrategy() throws Exception {
        Constructor<?> constructor = getStrategyConstructor();
        assertNotNull(constructor, "If the strategy pattern is implemented correctly, StockTradingManager should have a constructor that accepts a TradingStrategyType and TradingIndicatorStrategy object.");
        // Get all subtypes of TradingIndicatorStrategy using reflection
        Reflections reflections = new Reflections(StockManagerTest.class.getPackageName(), new SubTypesScanner(false));
        Set<Class<? extends TradingIndicatorStrategy>> subTypes = reflections.getSubTypesOf(TradingIndicatorStrategy.class);

        // Iterate over the subtypes
        for (Class<?> strategyClass : subTypes) {
            // Dynamically create an instance of the concrete strategy using reflection
            Constructor<?> strategyConstructor = strategyClass.getDeclaredConstructor();
            TradingIndicatorStrategy strategy = (TradingIndicatorStrategy) strategyConstructor.newInstance();

            // Create a pricing manager with the concrete strategy
            TradingStrategyType indicatorType = strategy.supportsType();
            StockTradingManager pricingManager = null;

            try {
                pricingManager = (StockTradingManager) constructor.newInstance(indicatorType, strategy);
            } catch (Exception e) {
                pricingManager = (StockTradingManager) constructor.newInstance(strategy);
            }

            // Call the adjust method on the pricing manager
            Stock rideDetails = new Stock(100.0, 60.0);
            Double indicator = pricingManager.calculateIndicator(rideDetails);

            if (indicatorType == TradingStrategyType.MOVING_AVERAGES) {
                assertEquals(80.0, indicator, "If the strategy pattern is implemented correctly, the calculateIndicator method of StockTradingManager should return the average of the current and previous price for the MOVING_AVERAGES strategy.");
            } else if (indicatorType == TradingStrategyType.MOMENTUM) {
                assertEquals(40.0, indicator, "If the strategy pattern is implemented correctly, the calculateIndicator method of StockTradingManager should return the difference between the current and previous price for the MOMENTUM strategy.");
            } else if (indicatorType == TradingStrategyType.VOLATILITY) {
                assertEquals(40.0, indicator, "If the strategy pattern is implemented correctly, the calculateIndicator method of StockTradingManager should return the absolute difference between the current and previous price for the VOLATILITY strategy.");
            }
        }
    }
}
