package com.assignment.question;

import com.assignment.question.services.AppService;
import com.assignment.question.services.EmailService;
import com.assignment.question.services.SmsService;
import com.assignment.question.utils.NotificationUtils;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Set;

import static org.assertj.core.api.Fail.fail;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.eq;

@ExtendWith(MockitoExtension.class)
public class StockTradingManagerTest {

    private static final Set<Class<?>> DEPENDENCIES = Set.of(EmailService.class, SmsService.class, AppService.class);

    @Test
    public void testDependencies() {

        Class<?> stockManagerClass = StockTradingManager.class;
        Field[] fields = stockManagerClass.getDeclaredFields();

        Arrays.stream(fields).forEach(field -> field.setAccessible(true));
        boolean anyDependencyPresent = DEPENDENCIES.stream().anyMatch(dependency -> Arrays.stream(fields).anyMatch(field -> field.getType().equals(dependency)));

        assertFalse(anyDependencyPresent, "If the observer pattern is implemented correctly, the StockTradingManager class should not have any dependencies");
    }

    @Test
    public void testObserverInterfaceMethod() {
        Class<?> observerInterface = Observer.class;
        Method[] methods = observerInterface.getDeclaredMethods();

        boolean hasMethod = Arrays.stream(methods)
                .anyMatch(method -> method.getParameterCount() == 2
                        && method.getParameterTypes()[0] == String.class
                        && method.getParameterTypes()[1] == double.class);

        assertTrue(hasMethod, "If the observer pattern is implemented correctly, the Observer interface should have a method to notify the observers with the stock name and the current price");
    }

    @Test
    public void testAddAndRemoveObserverMethod() {
        Class<?> publisherClass = Publisher.class;
        Method[] methods = publisherClass.getDeclaredMethods();

        long count = Arrays.stream(methods)
                .filter(method -> method.getParameterCount() == 1
                        && method.getParameterTypes()[0] == Observer.class)
                .count();

        assertTrue(count >= 2, "If the observer pattern is implemented correctly, the Publisher interface should have methods to add and remove observers");
    }

    @Test
    public void testConstructor() {
        Class<?> stockTradingManagerClass = StockTradingManager.class;
        try {
            Constructor<?> constructor = stockTradingManagerClass.getConstructor(String.class, double.class, double.class);
            assertNotNull(constructor, "The StockTradingManager class should have a constructor that takes the stock name, initial price and the notification threshold as arguments");
        } catch (NoSuchMethodException e) {
            fail("The StockTradingManager class should have a constructor that takes the stock name, initial price and the notification threshold as arguments");
        }
    }

    @Test
    public void testStockTradingManagerExtendsPublisher() {
        assertTrue(isSubclassOf(StockTradingManager.class, Publisher.class),
                "StockTradingManager should extend Publisher");
    }

    @Test
    public void testServicesImplementObserver() {

        assertTrue(implementsInterface(SmsService.class, Observer.class),
                "SmsService should implement Observer");
        assertTrue(implementsInterface(EmailService.class, Observer.class),
                "EmailService should implement Observer");
        assertTrue(implementsInterface(AppService.class, Observer.class),
                "AppService should implement Observer");
    }

    private boolean isSubclassOf(Class<?> subclass, Class<?> superclass) {
        return superclass.isAssignableFrom(subclass);
    }

    private boolean implementsInterface(Class<?> clazz, Class<?> interfaceClass) {
        return interfaceClass.isAssignableFrom(clazz);
    }


    @Test
    public void testSendNotification() {
        StockTradingManager stockTradingManager = new StockTradingManager(
                "ABC", 100.0, 150.0
        );
        stockTradingManager.addObserver(new EmailService());
        stockTradingManager.addObserver(new SmsService());
        stockTradingManager.addObserver(new AppService());
        try (MockedStatic<NotificationUtils> mockNotificationUtils = Mockito.mockStatic(NotificationUtils.class)) {

            stockTradingManager.updateStockPrice(160.0);

            mockNotificationUtils.verify(() -> NotificationUtils.sendEmail(eq("Price update for ABC"), eq("New price is 160.0")));
            mockNotificationUtils.verify(() -> NotificationUtils.sendSms(eq("Price update for ABC"), eq("New price is 160.0")));
            mockNotificationUtils.verify(() -> NotificationUtils.sendPush(eq("Price update for ABC"), eq("New price is 160.0")));
        }
    }
}
