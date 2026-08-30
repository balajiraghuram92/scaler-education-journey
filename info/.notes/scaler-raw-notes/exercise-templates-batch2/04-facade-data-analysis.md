# Facade Pattern for Data Analysis Application

Source folder: `1773391249_fdcca1ce0d8b83a0/Facade_Data-solution`

## Problem Statement

You are developing a software application for data analysis. The application involves data collection, preprocessing, analysis algorithms, and visualization. The interactions between these components can become complex. Your goal is to provide a simplified interface for data analysts to perform end-to-end analysis tasks without dealing with the inner workings of each component.

## Detailed Requirements

1. **Review the original workflow**: Take a closer look at the existing data analysis workflow and the interactions between different components.

2. **Create the facade class**: Create a new class called `DataAnalysisFacade` that implements the Facade pattern. This class will encapsulate the complex interactions between data collection, preprocessing, analysis algorithms, and visualization components.

3. **Remember to call the constructor of your facade using the same arguments from the existing components**: The constructor of your `DataAnalysisFacade` class should take the same arguments that the existing components require. This allows you to pass the necessary parameters to the facade.

4. **Test your implementation**: Test cases have been provided for you to verify your implementation. Run the test cases to ensure that your facade class works correctly and provides the expected functionality.

## Graded Contract (from tests)

The tests verify the following:

- **DataAnalysisManager** must NOT have any direct fields referencing: `DataCollectionService`, `DataPreprocessingService`, `AnalysisAlgorithmService`, or `VisualizationService`
- **DataAnalysisManager constructor** accepts 4 parameters in order:
  - `DataCollectionService`
  - `DataPreprocessingService`
  - `AnalysisAlgorithmService`
  - `VisualizationService`
- **performFullAnalysis(DataCollectionParams collectionParams, PreprocessingOptions preprocessingOptions, AnalysisAlgorithmConfig algorithmConfig) -> AnalysisResult** method exists
- When `performFullAnalysis()` is called, all of these must occur in sequence:
  - `dataCollectionService.collectData(collectionParams)` is called and returns `DataCollectionResult`
  - `dataPreprocessingService.preprocessData(data, preprocessingOptions)` is called and returns `PreprocessedData`
  - `algorithmService.applyAnalysisAlgorithms(preprocessedData, algorithmConfig)` is called and returns `AnalysisResult`
  - `visualizationService.visualizeResults(analysisResult)` is called

## Learner Template

```java
package com.assignment.question;

import com.assignment.question.models.*;
import com.assignment.question.services.*;

public class DataAnalysisManager {
    private DataAnalysisProcessor dataAnalysisProcessor;

    public DataAnalysisManager(DataCollectionService dataCollectionService,
                               DataPreprocessingService dataPreprocessingService,
                               AnalysisAlgorithmService analysisAlgorithmService,
                               VisualizationService visualizationService) {
        // TODO: initialize dataAnalysisProcessor with the dependencies
    }

    public AnalysisResult performFullAnalysis(DataCollectionParams collectionParams,
                                              PreprocessingOptions preprocessingOptions,
                                              AnalysisAlgorithmConfig algorithmConfig) {
        // TODO: delegate to dataAnalysisProcessor
    }
}
```

## Deliberately Left Out (for the learner to design)

- The initialization of `DataAnalysisProcessor` inside the constructor
- The delegation logic in `performFullAnalysis()` method to call `dataAnalysisProcessor.process()`
- The understanding that `DataAnalysisProcessor` encapsulates all the complex workflow steps
- The data flow between the different services (collection → preprocessing → analysis → visualization)
- The understanding that the facade pattern simplifies the client's interaction with a complex multi-step workflow
