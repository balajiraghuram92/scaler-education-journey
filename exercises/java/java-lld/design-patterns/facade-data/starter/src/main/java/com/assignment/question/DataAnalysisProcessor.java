package com.assignment.question;

import com.assignment.question.models.*;
import com.assignment.question.services.AnalysisAlgorithmService;
import com.assignment.question.services.DataCollectionService;
import com.assignment.question.services.DataPreprocessingService;
import com.assignment.question.services.VisualizationService;

public class DataAnalysisProcessor {

    private DataCollectionService dataCollectionService;
    private DataPreprocessingService dataPreprocessingService;
    private AnalysisAlgorithmService analysisAlgorithmService;
    private VisualizationService visualizationService;

    public DataAnalysisProcessor(DataCollectionService dataCollectionService,
                                 DataPreprocessingService dataPreprocessingService,
                                 AnalysisAlgorithmService analysisAlgorithmService,
                                 VisualizationService visualizationService) {
        this.dataCollectionService = dataCollectionService;
        this.dataPreprocessingService = dataPreprocessingService;
        this.analysisAlgorithmService = analysisAlgorithmService;
        this.visualizationService = visualizationService;
    }

    public AnalysisResult process(DataCollectionParams collectionParams,
                                  PreprocessingOptions preprocessingOptions,
                                  AnalysisAlgorithmConfig algorithmConfig) {
        // TODO: run the four-step pipeline in order — collect data, preprocess
        // the collected data's raw list, apply the analysis algorithms, then
        // visualize the analysis result before returning it.
        return null;
    }

}
