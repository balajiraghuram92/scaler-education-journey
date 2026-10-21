from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class DocumentType(Enum):
    TEXT = "text"
    SPREAD_SHEET = "spreadsheet"


@dataclass
class DocumentProcessor(ABC):
    document_name: str

    @abstractmethod
    def supports_type(self) -> DocumentType:
        pass


@dataclass
class TextDocumentProcessor(DocumentProcessor):
    def supports_type(self) -> DocumentType:
        return DocumentType.TEXT


@dataclass
class SpreadsheetDocumentProcessor(DocumentProcessor):
    def supports_type(self) -> DocumentType:
        return DocumentType.SPREAD_SHEET
