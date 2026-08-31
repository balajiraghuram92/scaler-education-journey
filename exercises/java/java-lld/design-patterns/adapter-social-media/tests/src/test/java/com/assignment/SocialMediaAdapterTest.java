package com.assignment;

import com.assignment.adapters.SocialMediaAdapter;
import com.assignment.api.ApiUtils;
import com.assignment.api.FacebookApi;
import com.assignment.api.TwitterApi;
import com.assignment.models.SocialMediaPost;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

@ExtendWith(MockitoExtension.class)
public class SocialMediaAdapterTest {

    @Test
    public void testMethods() {

        Class<?> adapterClass = SocialMediaAdapter.class;
        Method[] methods = adapterClass.getDeclaredMethods();

        assertTrue(methods.length >= 2,
                "If the adapter class is implemented correctly, there should be at least 2 methods.");

        long getPostsMethod = Arrays.stream(methods)
                .filter(method -> method.getParameterCount() == 2
                        && method.getParameterTypes()[0] == Long.class
                        && method.getParameterTypes()[1] == Long.class
                        && method.getReturnType() == List.class)
                .count();

        long postMethod = Arrays.stream(methods)
                .filter(method -> method.getParameterCount() == 2
                        && method.getParameterTypes()[0] == Long.class
                        && method.getParameterTypes()[1] == String.class
                        && method.getReturnType() == void.class)
                .count();

        assertEquals(1, getPostsMethod,
                "If the adapter class is implemented correctly, there should be 1 method for getting the list of posts which accepts 2 parameters of type Long and has a return type of List.");
        assertEquals(1, postMethod,
                "If the adapter class is implemented correctly, there should be 1 method for posting a message which accepts 2 parameters of type Long and String and has a return type of void.");
    }

    @Test
    public void testImplementations() {

        Reflections reflections = new Reflections(SocialMediaAdapterTest.class.getPackageName(),
                new SubTypesScanner(false));
        Set<Class<? extends SocialMediaAdapter>> adapterImplClasses = reflections
                .getSubTypesOf(SocialMediaAdapter.class);

        assertTrue(adapterImplClasses.size() >= 2,
                "If the adapter class is implemented correctly, there should be at least 2 implementations of the adapter interface.");

        for (Class<? extends SocialMediaAdapter> clazz : adapterImplClasses) {
            assertTrue(SocialMediaAdapter.class.isAssignableFrom(clazz),
                    "Class " + clazz.getSimpleName() + " should implement SocialMediaAdapter interface.");

            boolean hasApiReference = false;

            Field[] fields = clazz.getDeclaredFields();
            for (Field field : fields) {
                if ((field.getType() == FacebookApi.class || field.getType() == TwitterApi.class)) {
                    hasApiReference = true;
                    break;
                }
            }

            assertTrue(hasApiReference,
                    "If the adapter class is implemented correctly, it should have a field referring to the external APIs.");
        }
    }

    @Test
    public void testCommonPostClass() {
        Field[] fields = SocialMediaPost.class.getDeclaredFields();
        assertEquals(4, fields.length,
                "If the SocialMediaPost class is implemented correctly, it should have 4 fields.");
        int stringCount = Stream.of(fields)
                .filter(field -> field.getType() == String.class)
                .mapToInt(field -> 1)
                .sum();
        assertEquals(2, stringCount,
                "If the SocialMediaPost class is implemented correctly, it should have 2 fields of type String.");

        int longCount = Stream.of(fields)
                .filter(field -> field.getType() == Long.class)
                .mapToInt(field -> 1)
                .sum();
        assertEquals(2, longCount,
                "If the SocialMediaPost class is implemented correctly, it should have 2 field of type Long.");
    }

    @Test
    public void testGetPosts() throws Exception {
        Reflections reflections = new Reflections(SocialMediaAdapterTest.class.getPackageName(),
                new SubTypesScanner(false));
        Set<Class<? extends SocialMediaAdapter>> adapterClasses = reflections
                .getSubTypesOf(SocialMediaAdapter.class);

        List<Pair<SocialMediaAdapter, Method>> translateMethods = new ArrayList<>();

        for (Class<? extends SocialMediaAdapter> adapterClass : adapterClasses) {
            Constructor<? extends SocialMediaAdapter> constructor = adapterClass.getDeclaredConstructor();
            SocialMediaAdapter adapter = constructor.newInstance();

            Method[] methods = adapterClass.getDeclaredMethods();
            for (Method method : methods) {
                if (method.getParameterCount() == 2
                        && method.getParameterTypes()[0] == Long.class
                        && method.getParameterTypes()[1] == Long.class
                        && method.getReturnType() == List.class) {
                    translateMethods.add(new Pair<>(adapter, method));
                }
            }
        }

        try (MockedStatic<ApiUtils> mockApiUtils = Mockito.mockStatic(ApiUtils.class)) {
            for (Pair<SocialMediaAdapter, Method> method : translateMethods) {
                method.getRight().invoke(method.getLeft(), 1L, 123456789L);
            }

            mockApiUtils.verify(ApiUtils::logTwitterGetPosts);
            mockApiUtils.verify(ApiUtils::logFacebookGetPosts);

        }
    }

    @Test
    public void testPost() throws Exception {
        Reflections reflections = new Reflections(SocialMediaAdapter.class.getPackageName(),
                new SubTypesScanner(false));
        Set<Class<? extends SocialMediaAdapter>> adapterClasses = reflections
                .getSubTypesOf(SocialMediaAdapter.class);

        List<Pair<SocialMediaAdapter, Method>> translateMethods = new ArrayList<>();

        for (Class<? extends SocialMediaAdapter> adapterClass : adapterClasses) {
            Constructor<? extends SocialMediaAdapter> constructor = adapterClass.getDeclaredConstructor();
            SocialMediaAdapter adapter = constructor.newInstance();

            Method[] methods = adapterClass.getDeclaredMethods();
            for (Method method : methods) {
                if (method.getParameterCount() == 2
                        && method.getParameterTypes()[0] == Long.class
                        && method.getParameterTypes()[1] == String.class
                        && method.getReturnType() == void.class) {
                    translateMethods.add(new Pair<>(adapter, method));
                }
            }
        }
        try (MockedStatic<ApiUtils> mockApiUtils = Mockito.mockStatic(ApiUtils.class)) {
            for (Pair<SocialMediaAdapter, Method> method : translateMethods) {
                method.getRight().invoke(method.getLeft(), 1L, "Hello World");
            }

            mockApiUtils.verify(ApiUtils::logFacebookPostStatus);
            mockApiUtils.verify(ApiUtils::logTwitterPostStatus);

        }
    }

    private static class Pair<L, R> {
        private final L left;
        private final R right;

        private Pair(L left, R right) {
            this.left = left;
            this.right = right;
        }

        public L getLeft() {
            return left;
        }

        public R getRight() {
            return right;
        }

        public static <L, R> Pair<L, R> of(L left, R right) {
            return new Pair<>(left, right);
        }
    }
}
