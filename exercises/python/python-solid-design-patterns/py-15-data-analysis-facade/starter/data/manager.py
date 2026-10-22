from .model import *
from .processor import DataAnalysisProcessor
from .services import *


class DataAnalysisManager:
    def __init__(
        self,
        data_collection_service: DataCollectionService,
        data_preprocessing_service: DataPreprocessingService,
        analysis_algorithm_service: AnalysisAlgorithmService,
        visualization_service: VisualizationService,
    ):
        self.processor = DataAnalysisProcessor(
            data_collection_service,
            data_preprocessing_service,
            analysis_algorithm_service,
            visualization_service,
        )

    def perform_full_analysis(
        self,
        collection_params: DataCollectionParams,
        preprocessing_options: PreprocessingOptions,
        algorithm_config: AnalysisAlgorithmConfig,
    ) -> AnalysisResult:
        return self.processor.process(
            collection_params, preprocessing_options, algorithm_config
        )
