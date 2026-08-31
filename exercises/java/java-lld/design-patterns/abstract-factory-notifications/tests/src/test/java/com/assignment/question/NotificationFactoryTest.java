package com.assignment.question;

import com.assignment.question.notification.EmailNotification;
import com.assignment.question.notification.Notification;
import com.assignment.question.sender.NotificationSender;
import com.assignment.question.template.EmailNotificationTemplate;
import com.assignment.question.template.NotificationTemplate;
import org.junit.jupiter.api.Test;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

public class NotificationFactoryTest {

    @Test
    public void testAbstractFactoryClass() {
        // Define the package where your files are located
        String packageName = NotificationFactoryTest.class.getPackageName();

        // Get all subtypes of NotificationFactory using reflection
        Reflections reflections = new Reflections(packageName, new SubTypesScanner(false));
        Set<Class<? extends NotificationFactory>> subTypes = reflections.getSubTypesOf(NotificationFactory.class);

        assertEquals(2, subTypes.size(),
                "If the abstract factory is implemented correctly, it should have 2 subtypes: EmailNotificationFactory and PushNotificationFactory.");

        boolean hasSupportsType = Arrays.stream(NotificationFactory.class.getDeclaredMethods())
                .anyMatch(method -> method.getName().equals("notificationType")
                        && method.getParameterCount() == 0
                        && method.getReturnType().equals(NotificationType.class)
                        && Modifier.isAbstract(method.getModifiers()));
        assertTrue(hasSupportsType,
                "If the abstract factory class is implemented correctly, it should have a method called notificationType that takes no parameters and returns a NotificationType.");

        boolean hasCreateNotificationMethod = Arrays.stream(NotificationFactory.class.getDeclaredMethods())
                .anyMatch(method -> Modifier.isAbstract(method.getModifiers())
                        && method.getReturnType().equals(Notification.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class)
                        && Arrays.asList(method.getParameterTypes()).contains(NotificationTemplate.class));
        assertTrue(hasCreateNotificationMethod,
                "If the abstract factory class is implemented correctly, it should have a method to create a notification that takes a String parameter recipient and a NotificationTemplate parameter template and returns a Notification.");

        boolean hasCreateTemplateMethod = Arrays.stream(NotificationFactory.class.getDeclaredMethods())
                .anyMatch(method -> Modifier.isAbstract(method.getModifiers())
                        && method.getReturnType().equals(NotificationTemplate.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class));
        assertTrue(hasCreateTemplateMethod,
                "If the abstract factory class is implemented correctly, it should have a method to create a notification template that takes a String parameter template name and returns a NotificationTemplate.");

        boolean hasCreateSenderMethod = Arrays.stream(NotificationFactory.class.getDeclaredMethods())
                .anyMatch(method -> Modifier.isAbstract(method.getModifiers())
                        && method.getReturnType().equals(NotificationSender.class)
                        && Arrays.asList(method.getParameterTypes()).contains(Notification.class));
        assertTrue(hasCreateSenderMethod,
                "If the abstract factory class is implemented correctly, it should have a method to create a notification sender that takes a Notification parameter notification and returns a NotificationSender.");

    }

    @Test
    public void testNotificationCreateMethodInvocation() {
        // Get all methods in NotificationFactory
        Method[] methods = NotificationFactory.class.getDeclaredMethods();

        // Check if any method is returning a DocumentProcessor
        Method createMethod = Arrays.stream(methods)
                .filter(method -> method.getReturnType().equals(Notification.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class)
                        && Arrays.asList(method.getParameterTypes()).contains(NotificationTemplate.class))
                .findFirst()
                .orElse(null);

        assertNotNull(createMethod,
                "If the abstract factory is implemented correctly, it should have a method to create a notification that takes a String parameter recipient and a NotificationTemplate parameter template and returns a Notification.");

        String recipient = "test";
        String sender = "sender";
        NotificationTemplate template = new EmailNotificationTemplate("test");

        // Invoke the create method with parameters in different orders
        Notification notification = null;

        try {
            notification = (Notification) createMethod.invoke(new EmailNotificationFactory(), recipient, sender, template);
        } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
            fail("If the abstract factory is implemented correctly, the create method for a notification should take a String parameter recipient and a NotificationTemplate parameter template and return a Notification.");
        }

        // Verify that the returned processors are not null and match the expected type
        assertNotNull(notification,
                "If the abstract factory is implemented correctly, the create method for a notification should return a non-null Notification.");
        assertEquals(NotificationType.EMAIL, notification.notificationType(),
                "If the factory is implemented correctly, the create method should return an EmailNotification for an email notification.");

    }

    @Test
    public void testTemplateCreateMethodInvocation() {
        // Get all methods in NotificationFactory
        Method[] methods = NotificationFactory.class.getDeclaredMethods();

        // Check if any method is returning a NotificationTemplate
        Method createMethod = Arrays.stream(methods)
                .filter(method -> method.getReturnType().equals(NotificationTemplate.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class))
                .findFirst()
                .orElse(null);

        assertNotNull(createMethod,
                "If the abstract factory is implemented correctly, it should have a method to create a notification template that takes a String parameter message and returns a NotificationTemplate.");

        String message = "test";

        // Invoke the create method with parameters in different orders
        NotificationTemplate template = null;

        try {
            template = (NotificationTemplate) createMethod.invoke(new EmailNotificationFactory(), message);
        } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
            fail("If the abstract factory is implemented correctly, the create method for a notification template should take a String parameter message and return a NotificationTemplate.");
        }

        // Verify that the returned processors are not null and match the expected type
        assertNotNull(template,
                "If the abstract factory is implemented correctly, the create method for a document parser should return a non-null DocumentParser.");
        assertEquals(NotificationType.EMAIL, template.notificationType(),
                "If the factory is implemented correctly, the create method should return a TextDocumentParser for a text document.");

    }

    @Test
    public void testSenderCreateMethodInvocation() {
        // Get all methods in NotificationFactory
        Method[] methods = NotificationFactory.class.getDeclaredMethods();

        // Check if any method is returning a NotificationSender
        Method createMethod = Arrays.stream(methods)
                .filter(method -> method.getReturnType().equals(NotificationSender.class)
                        && Arrays.asList(method.getParameterTypes()).contains(Notification.class))
                .findFirst()
                .orElse(null);

        assertNotNull(createMethod,
                "If the abstract factory is implemented correctly, it should have a method to create a notification sender that takes a Notification parameter notification and returns a NotificationSender.");

        Notification notification = new EmailNotification("test", "sender", new EmailNotificationTemplate("test"));
        NotificationSender sender = null;

        try {
            sender = (NotificationSender) createMethod.invoke(new EmailNotificationFactory(), notification);
        } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
            fail("If the abstract factory is implemented correctly, the create method for a notification sender should take a Notification parameter notification and return a NotificationSender.");
        }

        // Verify that the returned processors are not null and match the expected type
        assertNotNull(sender,
                "If the abstract factory is implemented correctly, the create method for a notification sender should return a non-null NotificationSender.");
        assertEquals(NotificationType.EMAIL, sender.notificationType(),
                "If the factory is implemented correctly, the create method should take a Notification parameter notification and return a TextNotificationSender for a text notification.");

    }

}
