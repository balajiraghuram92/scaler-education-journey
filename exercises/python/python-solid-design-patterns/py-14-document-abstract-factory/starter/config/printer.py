from abc import ABC, abstractmethod
from dataclasses import dataclass

from .processor import DocumentProcessor, DocumentType


@dataclass
class DocumentPrinter(ABC):
    processor: DocumentProcessor

    @abstractmethod
    def supports_type(self) -> DocumentType:
        pass


@dataclass
class TextDocumentPrinter(DocumentPrinter):
    def supports_type(self) -> DocumentType:
        return DocumentType.TEXT


@dataclass
class SpreadsheetDocumentPrinter(DocumentPrinter):
    def supports_type(self) -> DocumentType:
        return DocumentType.SPREAD_SHEET
