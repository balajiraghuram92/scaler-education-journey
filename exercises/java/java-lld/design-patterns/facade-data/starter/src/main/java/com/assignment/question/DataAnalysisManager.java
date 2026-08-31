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
    // TODO: this class must NOT hold direct fields of DataCollectionService,
    // DataPreprocessingService, AnalysisAlgorithmService, or VisualizationService —
    // delegate the actual work to DataAnalysisProcessor instead.

    public DataAnalysisManager(DataCollectionService dataCollectionService,
                               DataPreprocessingService dataPreprocessingService,
                               AnalysisAlgorithmService analysisAlgorithmService,
                               VisualizationService visualizationService) {
        // TODO: construct the internal DataAnalysisProcessor from these dependencies
    }

    public AnalysisResult performFullAnalysis(DataCollectionParams collectionParams,
                                              PreprocessingOptions preprocessingOptions,
                                              AnalysisAlgorithmConfig algorithmConfig) {
        // TODO: delegate to the internal DataAnalysisProcessor
        return null;
    }

}
