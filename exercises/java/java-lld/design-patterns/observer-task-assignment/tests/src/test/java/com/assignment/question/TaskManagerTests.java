package com.assignment.question;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

import com.assignment.question.services.AppService;
import com.assignment.question.services.EmailService;
import com.assignment.question.services.SlackService;
import com.assignment.question.utils.NotificationUtils;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Set;

import static org.assertj.core.api.Fail.fail;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.eq;

@ExtendWith(MockitoExtension.class)
public class TaskManagerTests {

    private static final Set<Class<?>> DEPENDENCIES = Set.of(EmailService.class, SlackService.class, AppService.class);

    @Test
    public void testDependencies() {

        Class<?> managerClass = TaskManager.class;
        Field[] fields = managerClass.getDeclaredFields();

        Arrays.stream(fields).forEach(field -> field.setAccessible(true));
        boolean anyDependencyPresent = DEPENDENCIES.stream().anyMatch(dependency -> Arrays.stream(fields).anyMatch(field -> field.getType().equals(dependency)));

        assertFalse(anyDependencyPresent, "If the observer pattern is implemented correctly, the TaskManager class should not have any dependencies");
    }

    @Test
    public void testObserverInterfaceMethod() {
        Class<?> observerInterface = Observer.class;
        Method[] methods = observerInterface.getDeclaredMethods();

        boolean hasMethod = Arrays.stream(methods).anyMatch(method -> method.getParameterCount() == 2 && method.getParameterTypes()[0] == Long.class && method.getParameterTypes()[1] == Long.class);

        assertTrue(hasMethod, "If the observer pattern is implemented correctly, the Observer interface should have a method to notify the observers with the task and user ID");
    }

    @Test
    public void testAddAndRemoveObserverMethod() {
        Class<?> publisherClass = Publisher.class;
        Method[] methods = publisherClass.getDeclaredMethods();

        long count = Arrays.stream(methods).filter(method -> method.getParameterCount() == 1 && method.getParameterTypes()[0] == Observer.class).count();

        assertTrue(count >= 2, "If the observer pattern is implemented correctly, the Publisher interface should have methods to add and remove observers");
    }

    @Test
    public void testConstructor() {
        Class<?> stockTradingManagerClass = TaskManager.class;
        try {
            Constructor<?> constructor = stockTradingManagerClass.getConstructor();
            assertNotNull(constructor, "The TaskManager class should have a default constructor");
        } catch (NoSuchMethodException e) {
            fail("The TaskManager class should have a default constructor");
        }
    }

    @Test
    public void testStockTradingManagerExtendsPublisher() {
        assertTrue(isSubclassOf(TaskManager.class, Publisher.class), "StockTradingManager should extend Publisher");
    }

    @Test
    public void testServicesImplementObserver() {

        assertTrue(implementsInterface(SlackService.class, Observer.class), "SlackService should implement Observer");
        assertTrue(implementsInterface(EmailService.class, Observer.class), "EmailService should implement Observer");
        assertTrue(implementsInterface(AppService.class, Observer.class), "AppService should implement Observer");
    }

    private boolean isSubclassOf(Class<?> subclass, Class<?> superclass) {
        return superclass.isAssignableFrom(subclass);
    }

    private boolean implementsInterface(Class<?> clazz, Class<?> interfaceClass) {
        return interfaceClass.isAssignableFrom(clazz);
    }


    @Test
    public void testSendNotification() {
        TaskManager taskManager = new TaskManager();
        taskManager.addObserver(new EmailService());
        taskManager.addObserver(new SlackService());
        taskManager.addObserver(new AppService());
        try (MockedStatic<NotificationUtils> mockNotificationUtils = Mockito.mockStatic(NotificationUtils.class)) {

            taskManager.assignTask(1L, 2L);

            mockNotificationUtils.verify(() -> NotificationUtils.sendEmail(eq("New task assigned"), eq("Task 1 assigned to user 2")));
            mockNotificationUtils.verify(() -> NotificationUtils.sendSlack(eq("New task assigned"), eq("Task 1 assigned to user 2")));
            mockNotificationUtils.verify(() -> NotificationUtils.sendPush(eq("New task assigned"), eq("Task 1 assigned to user 2")));
        }
    }
}
