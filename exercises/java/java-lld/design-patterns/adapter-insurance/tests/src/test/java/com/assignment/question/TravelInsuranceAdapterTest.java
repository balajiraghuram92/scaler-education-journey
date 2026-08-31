package com.assignment.question;

import com.assignment.question.external.AutoProtectApi;
import com.assignment.question.external.TravelGuardApi;
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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

@ExtendWith(MockitoExtension.class)
public class TravelInsuranceAdapterTest {

    @Test
    public void testMethods() {

        Class<?> adapterClass = TravelInsuranceAdapter.class;
        Method[] methods = adapterClass.getDeclaredMethods();

        assertTrue(methods.length >= 2, "If the adapter class is implemented correctly, there should be at least 2 methods.");

        long addClaimMethodCount = Arrays.stream(methods)
                .filter(method -> method.getParameterCount() == 2
                        && method.getReturnType() == void.class
                        && method.getParameterTypes()[0] == String.class
                        && List.of(double.class, Double.class).contains(method.getParameterTypes()[1]))
                .count();

        long statusMethodCount = Arrays.stream(methods)
                .filter(method -> method.getParameterCount() == 1
                        && method.getReturnType() != void.class
                        && method.getParameterTypes()[0] == String.class)
                .count();

        assertEquals(1, addClaimMethodCount, "If the adapter class is implemented correctly, there should be 1 method for adding a claim which accepts an ID and amount.");
        assertEquals(1, statusMethodCount, "If the adapter class is implemented correctly, there should be 1 method for getting the status of a claim which accepts an ID and has a non-void return type.");
    }

    @Test
    public void testImplementations() {

        Reflections reflections = new Reflections(TravelInsuranceAdapterTest.class.getPackageName(), new SubTypesScanner(false));
        Set<Class<? extends TravelInsuranceAdapter>> adapterImplClasses = reflections.getSubTypesOf(TravelInsuranceAdapter.class);

        assertTrue(adapterImplClasses.size() >= 2, "If the adapter class is implemented correctly, there should be at least 2 implementations of the adapter interface.");

        for (Class<? extends TravelInsuranceAdapter> clazz : adapterImplClasses) {
            assertTrue(TravelInsuranceAdapter.class.isAssignableFrom(clazz), "Class " + clazz.getSimpleName() + " should implement TravelInsuranceAdapter interface.");

            boolean hasApiReference = false;

            Field[] fields = clazz.getDeclaredFields();
            for (Field field : fields) {
                if ((field.getType() == AutoProtectApi.class || field.getType() == TravelGuardApi.class)) {
                    hasApiReference = true;
                    break;
                }
            }

            assertTrue(hasApiReference, "If the adapter class is implemented correctly, it should have a field referring to the external APIs.");
        }
    }

    @Test
    public void testAddClaim() throws Exception {
        Reflections reflections = new Reflections(TravelInsuranceAdapterTest.class.getPackageName(), new SubTypesScanner(false));
        Set<Class<? extends TravelInsuranceAdapter>> adapterClasses = reflections.getSubTypesOf(TravelInsuranceAdapter.class);

        List<Pair<TravelInsuranceAdapter, Method>> claimMethods = new ArrayList<>();

        for (Class<? extends TravelInsuranceAdapter> adapterClass : adapterClasses) {
            Constructor<? extends TravelInsuranceAdapter> constructor = adapterClass.getDeclaredConstructor();
            TravelInsuranceAdapter adapter = constructor.newInstance();

            Method[] methods = adapterClass.getDeclaredMethods();
            for (Method method : methods) {
                if (method.getReturnType() == void.class
                        && method.getParameterTypes().length == 2
                        && method.getParameterTypes()[0] == String.class
                        && List.of(double.class, Double.class).contains(method.getParameterTypes()[1])) {

                    claimMethods.add(new Pair<>(adapter, method));
                }
            }
        }

        try (MockedStatic<ApiUtils> mockApiUtils = Mockito.mockStatic(ApiUtils.class)) {
            for (Pair<TravelInsuranceAdapter, Method> claimMethod : claimMethods) {
                claimMethod.getRight().invoke(claimMethod.getLeft(), "reference", 100.0);
            }

            mockApiUtils.verify(ApiUtils::logAutoProtectClaimCall);
            mockApiUtils.verify(ApiUtils::logTravelGuardClaimCall);

        }
    }

    @Test
    public void testGetStatus() throws Exception {
        Reflections reflections = new Reflections(TravelInsuranceAdapterTest.class.getPackageName(), new SubTypesScanner(false));
        Set<Class<? extends TravelInsuranceAdapter>> adapterClasses = reflections.getSubTypesOf(TravelInsuranceAdapter.class);

        List<Pair<TravelInsuranceAdapter, Method>> claimMethods = new ArrayList<>();

        for (Class<? extends TravelInsuranceAdapter> adapterClass : adapterClasses) {
            Constructor<? extends TravelInsuranceAdapter> constructor = adapterClass.getDeclaredConstructor();
            TravelInsuranceAdapter adapter = constructor.newInstance();

            Method[] methods = adapterClass.getDeclaredMethods();
            for (Method method : methods) {
                if (method.getReturnType() != void.class
                        && method.getParameterTypes().length == 1
                        && method.getParameterTypes()[0] == String.class) {

                    claimMethods.add(new Pair<>(adapter, method));
                }
            }
        }
        try (MockedStatic<ApiUtils> mockApiUtils = Mockito.mockStatic(ApiUtils.class)) {
            for (Pair<TravelInsuranceAdapter, Method> claimMethod : claimMethods) {
                claimMethod.getRight().invoke(claimMethod.getLeft(), "reference");
            }

            mockApiUtils.verify(ApiUtils::logAutoProtectStatusCall);
            mockApiUtils.verify(ApiUtils::logTravelGuardStatusCall);

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
