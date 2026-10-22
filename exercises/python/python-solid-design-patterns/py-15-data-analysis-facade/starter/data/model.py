from dataclasses import dataclass, field
from typing import List


@dataclass
class AnalysisAlgorithmConfig:
    pass


@dataclass
class AnalysisResult:
    pass


@dataclass
class PreprocessingOptions:
    pass


@dataclass
class PreprocessedData:
    pass


@dataclass
class DataCollectionResult:
    data: List[object] = field(default_factory=list)


@dataclass
class DataCollectionParams:
    pass
