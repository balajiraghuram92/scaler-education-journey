from abc import ABC, abstractmethod
from dataclasses import dataclass

from .processor import DocumentType


@dataclass
class DocumentParser(ABC):
    path: str

    @abstractmethod
    def supports_type(self) -> DocumentType:
        pass


@dataclass
class TextDocumentParser(DocumentParser):
    def supports_type(self) -> DocumentType:
        return DocumentType.TEXT


@dataclass
class SpreadsheetDocumentParser(DocumentParser):
    def supports_type(self) -> DocumentType:
        return DocumentType.SPREAD_SHEET
