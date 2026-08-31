package com.assignment.question;

import com.assignment.question.models.AnalysisAlgorithmConfig;
import com.assignment.question.models.AnalysisResult;
import com.assignment.question.models.DataCollectionParams;
import com.assignment.question.models.PreprocessingOptions;
import com.assignment.question.services.AnalysisAlgorithmService;
import com.assignment.question.services.DataCollectionService;
import com.assignment.question.services.DataPreprocessingService;
import com.assignment.question.services.VisualizationService;

public class DataAnalysisManager {

    private DataAnalysisProcessor dataAnalysisProcessor;

    public DataAnalysisManager(DataCollectionService dataCollectionService,
                               DataPreprocessingService dataPreprocessingService,
                               AnalysisAlgorithmService analysisAlgorithmService,
                               VisualizationService visualizationService) {
        dataAnalysisProcessor = new DataAnalysisProcessor(dataCollectionService, dataPreprocessingService, analysisAlgorithmService, visualizationService);
    }

    public AnalysisResult performFullAnalysis(DataCollectionParams collectionParams,
                                              PreprocessingOptions preprocessingOptions,
                                              AnalysisAlgorithmConfig algorithmConfig) {
        return dataAnalysisProcessor.process(collectionParams, preprocessingOptions, algorithmConfig);
    }

}
