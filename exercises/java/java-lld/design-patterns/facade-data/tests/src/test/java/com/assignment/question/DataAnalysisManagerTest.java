package com.assignment.question;

import com.assignment.question.models.*;
import com.assignment.question.services.AnalysisAlgorithmService;
import com.assignment.question.services.DataCollectionService;
import com.assignment.question.services.DataPreprocessingService;
import com.assignment.question.services.VisualizationService;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.Collections;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.Mockito.*;

public class DataAnalysisManagerTest {

    private static final Set<Class<?>> DEPENDENCIES = Set.of(DataCollectionService.class, DataPreprocessingService.class, AnalysisAlgorithmService.class, VisualizationService.class);

    @Test
    public void testDependencies() {

        Class<?> bookingManagerClass = DataAnalysisManager.class;
        Field[] fields = bookingManagerClass.getDeclaredFields();

        Arrays.stream(fields).forEach(field -> field.setAccessible(true));


        boolean anyDependencyPresent = DEPENDENCIES.stream().anyMatch(dependency -> Arrays.stream(fields).anyMatch(field -> field.getType().equals(dependency)));

        assertFalse(anyDependencyPresent, "If the facade pattern is implemented correctly, the DataAnalysisManager class should not have any dependencies");
    }

    @Test
    public void testDataProcess() {

        DataCollectionParams dataCollectionParams = new DataCollectionParams();
        PreprocessingOptions preprocessingOptions = new PreprocessingOptions();
        AnalysisAlgorithmConfig algorithmConfig = new AnalysisAlgorithmConfig();
        PreprocessedData preprocessedData = new PreprocessedData();
        AnalysisResult analysisResult = new AnalysisResult();

        // Mock the dependencies
        DataCollectionService dataCollectionService = mock(DataCollectionService.class);
        when(dataCollectionService.collectData(dataCollectionParams)).thenReturn(new DataCollectionResult());

        DataPreprocessingService dataPreprocessingService = mock(DataPreprocessingService.class);

        when(dataPreprocessingService.preprocessData(anyList(), eq(preprocessingOptions))).thenReturn(preprocessedData);

        AnalysisAlgorithmService algorithmService = mock(AnalysisAlgorithmService.class);
        when(algorithmService.applyAnalysisAlgorithms(preprocessedData, algorithmConfig)).thenReturn(analysisResult);

        VisualizationService visualizationService = mock(VisualizationService.class);

        // Create a BookingManager instance with mocked dependencies
        DataAnalysisManager dataAnalysisManager = new DataAnalysisManager(dataCollectionService, dataPreprocessingService, algorithmService, visualizationService);


        dataAnalysisManager.performFullAnalysis(dataCollectionParams, preprocessingOptions, algorithmConfig);

        String errorPattern = "If the facade pattern is implemented correctly, the %s method should be called on the %s dependency";
        // Verify interactions with the dependencies
        verify(dataCollectionService, Mockito.description(String.format(errorPattern, "checkAvailability", "AvailabilityService"))).collectData(dataCollectionParams);
        verify(dataPreprocessingService).preprocessData(Collections.emptyList(), preprocessingOptions);

        verify(algorithmService, Mockito.description(String.format(errorPattern, "updateLoyaltyPoints", "LoyaltyService"))).applyAnalysisAlgorithms(preprocessedData, algorithmConfig);
        verify(visualizationService, Mockito.description(String.format(errorPattern, "updateAccommodationDetails", "AccommodationDetailsService"))).visualizeResults(analysisResult);
    }

}
