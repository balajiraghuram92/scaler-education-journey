package com.assignment.question;

import com.assignment.question.services.HumidityService;
import com.assignment.question.services.PressureService;
import com.assignment.question.services.TemperatureService;
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

@ExtendWith(MockitoExtension.class)
public class WeatherMonitorTests {

    private static final Set<Class<?>> DEPENDENCIES = Set.of(TemperatureService.class, HumidityService.class, PressureService.class);

    @Test
    public void testDependencies() {

        Class<?> stockManagerClass = WeatherMonitoringApplication.class;
        Field[] fields = stockManagerClass.getDeclaredFields();

        Arrays.stream(fields).forEach(field -> field.setAccessible(true));
        boolean anyDependencyPresent = DEPENDENCIES.stream().anyMatch(dependency -> Arrays.stream(fields).anyMatch(field -> field.getType().equals(dependency)));

        assertFalse(anyDependencyPresent, "If the observer pattern is implemented correctly, the WeatherMonitoringApplication class should not have any dependencies");
    }

    @Test
    public void testObserverInterfaceMethod() {
        Class<?> observerInterface = Observer.class;
        Method[] methods = observerInterface.getDeclaredMethods();

        boolean hasMethod = Arrays.stream(methods)
                .anyMatch(method -> method.getParameterCount() == 1
                        && method.getParameterTypes()[0] == double.class);

        assertTrue(hasMethod, "If the observer pattern is implemented correctly, the Observer interface should have a method to notify the observers with the new value");
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
        Class<?> stockTradingManagerClass = WeatherMonitoringApplication.class;
        try {
            Constructor<?> constructor = stockTradingManagerClass.getConstructor(double.class, double.class, double.class, double.class, double.class, double.class);
            assertNotNull(constructor, "The WeatherMonitoringApplication class should have a constructor that takes the temperature, humidity and pressure and the notification thresholds for each as arguments");
        } catch (NoSuchMethodException e) {
            fail("The WeatherMonitoringApplication class should have a constructor that takes the temperature, humidity and pressure and the notification thresholds for each as arguments");
        }
    }

    @Test
    public void testStockTradingManagerExtendsPublisher() {
        assertTrue(isSubclassOf(WeatherMonitoringApplication.class, Publisher.class),
                "WeatherMonitoringApplication should extend Publisher");
    }

    @Test
    public void testServicesImplementObserver() {

        assertTrue(implementsInterface(TemperatureService.class, Observer.class),
                "TemperatureService should implement Observer");
        assertTrue(implementsInterface(HumidityService.class, Observer.class),
                "HumidityService should implement Observer");
        assertTrue(implementsInterface(PressureService.class, Observer.class),
                "PressureService should implement Observer");
    }

    private boolean isSubclassOf(Class<?> subclass, Class<?> superclass) {
        return superclass.isAssignableFrom(subclass);
    }

    private boolean implementsInterface(Class<?> clazz, Class<?> interfaceClass) {
        return interfaceClass.isAssignableFrom(clazz);
    }


    @Test
    public void testSendNotification() {
        WeatherMonitoringApplication weatherMonitor = new WeatherMonitoringApplication(
                100.0, 200.0, 300.0, 110.0, 210.0, 310.0
        );
        weatherMonitor.addObserver(new TemperatureService());
        weatherMonitor.addObserver(new HumidityService());
        weatherMonitor.addObserver(new PressureService());
        try (MockedStatic<NotificationUtils> mockNotificationUtils = Mockito.mockStatic(NotificationUtils.class)) {

            weatherMonitor.updateWeatherConditions(120.0, 220.0, 320.0);

            String message = "New value is %.1f";
            mockNotificationUtils.verify(() -> NotificationUtils.sendNotification(message.formatted(120.0)), Mockito.times(3));
        }
    }
}
