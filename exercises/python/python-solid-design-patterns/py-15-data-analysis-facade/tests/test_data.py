import pytest

from data.manager import DataAnalysisManager
from data.model import (
    AnalysisAlgorithmConfig,
    AnalysisResult,
    DataCollectionParams,
    DataCollectionResult,
    PreprocessedData,
    PreprocessingOptions,
)
from data.processor import DataAnalysisProcessor
from data.services import (
    AnalysisAlgorithmService,
    DataCollectionService,
    DataPreprocessingService,
    VisualizationService,
)


class Rig:
    """Four recording fakes that share one call log and pass distinct objects along."""

    def __init__(self):
        self.log = []
        self.raw = [object(), object()]
        self.collected = DataCollectionResult(self.raw)
        self.preprocessed = PreprocessedData()
        self.result = AnalysisResult()
        rig = self

        class Collect:
            def collect_data(self, params):
                rig.log.append(("collect", params))
                return rig.collected

        class Prep:
            def preprocess_data(self, raw_data, options):
                rig.log.append(("preprocess", raw_data, options))
                return rig.preprocessed

        class Algo:
            def apply_analysis_algorithms(self, data, config):
                rig.log.append(("analyse", data, config))
                return rig.result

        class Viz:
            def visualize_results(self, result):
                rig.log.append(("visualize", result))

        self.services = (Collect(), Prep(), Algo(), Viz())
        self.params, self.options, self.config = (
            DataCollectionParams(), PreprocessingOptions(), AnalysisAlgorithmConfig(),
        )

    def names(self):
        return [e[0] for e in self.log]


def test_manager_does_not_expose_the_services():
    manager = DataAnalysisManager(
        DataCollectionService(), DataPreprocessingService(),
        AnalysisAlgorithmService(), VisualizationService(),
    )
    for name in ("data_collection_service", "data_preprocessing_service",
                 "analysis_algorithm_service", "visualization_service"):
        assert not hasattr(manager, name), f"DataAnalysisManager must not expose {name}"


def test_pipeline_runs_in_order():
    rig = Rig()
    DataAnalysisProcessor(*rig.services).process(rig.params, rig.options, rig.config)
    assert rig.names() == ["collect", "preprocess", "analyse", "visualize"], f"wrong order: {rig.names()}"


def test_data_flows_from_each_stage_into_the_next():
    rig = Rig()
    DataAnalysisProcessor(*rig.services).process(rig.params, rig.options, rig.config)
    by_name = {e[0]: e for e in rig.log}
    assert by_name["preprocess"][1] is rig.raw, "preprocess_data must receive collection_result.data, not the result object"
    assert by_name["analyse"][1] is rig.preprocessed, "analysis must receive the preprocessed data"
    assert by_name["visualize"][1] is rig.result, "visualisation must receive the analysis result"


def test_params_options_and_config_are_forwarded_untouched():
    rig = Rig()
    DataAnalysisProcessor(*rig.services).process(rig.params, rig.options, rig.config)
    by_name = {e[0]: e for e in rig.log}
    assert by_name["collect"][1] is rig.params
    assert by_name["preprocess"][2] is rig.options
    assert by_name["analyse"][2] is rig.config


def test_returns_the_analysis_result():
    rig = Rig()
    out = DataAnalysisProcessor(*rig.services).process(rig.params, rig.options, rig.config)
    assert out is rig.result, "process() must return the AnalysisResult from the algorithm service"


def test_constructor_order_matches_the_manager():
    rig = Rig()
    manager = DataAnalysisManager(*rig.services)
    out = manager.perform_full_analysis(rig.params, rig.options, rig.config)
    assert out is rig.result
    assert rig.names() == ["collect", "preprocess", "analyse", "visualize"], (
        "services must be wired in the order collection, preprocessing, algorithm, visualisation"
    )


def test_failure_in_a_stage_stops_the_pipeline():
    rig = Rig()

    class Boom:
        def preprocess_data(self, raw_data, options):
            rig.log.append(("preprocess", raw_data, options))
            raise RuntimeError("bad data")

    services = (rig.services[0], Boom(), rig.services[2], rig.services[3])
    with pytest.raises(RuntimeError, match="bad data"):
        DataAnalysisProcessor(*services).process(rig.params, rig.options, rig.config)
    assert rig.names() == ["collect", "preprocess"], "later stages must not run after a failure, and the error must propagate"


def test_works_with_the_default_services():
    manager = DataAnalysisManager(
        DataCollectionService(), DataPreprocessingService(),
        AnalysisAlgorithmService(), VisualizationService(),
    )
    out = manager.perform_full_analysis(DataCollectionParams(), PreprocessingOptions(), AnalysisAlgorithmConfig())
    assert isinstance(out, AnalysisResult)
