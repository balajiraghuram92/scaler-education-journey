from .model import *
from .services import *


class DataAnalysisProcessor:
    """Facade over the four analysis services.

    __init__ takes data_collection_service, data_preprocessing_service,
    analysis_algorithm_service and visualization_service (the same order as
    DataAnalysisManager.__init__). Services are injected, never created here.
    """

    def __init__(
        self,
        data_collection_service: DataCollectionService,
        data_preprocessing_service: DataPreprocessingService,
        analysis_algorithm_service: AnalysisAlgorithmService,
        visualization_service: VisualizationService,
    ):
        raise NotImplementedError("Store the four services")

    def process(
        self,
        collection_params: DataCollectionParams,
        preprocessing_options: PreprocessingOptions,
        algorithm_config: AnalysisAlgorithmConfig,
    ) -> AnalysisResult:
        """Run the pipeline in order:

        1. collect_data(collection_params)
        2. preprocess_data(collection_result.data, preprocessing_options)
        3. apply_analysis_algorithms(preprocessed_data, algorithm_config)
        4. visualize_results(analysis_result)
        5. return the AnalysisResult
        """
        raise NotImplementedError("Implement the pipeline")
