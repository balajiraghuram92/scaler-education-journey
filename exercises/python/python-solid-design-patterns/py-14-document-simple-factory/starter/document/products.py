from abc import ABC
from dataclasses import dataclass
from enum import Enum


class DocumentType(Enum):
    PRESENTATION = "Presentation"
    SPREADSHEET = "Spreadsheet"
    TEXT = "Text"


@dataclass
class DocumentProcessor(ABC):
    """Base product with a ``document_name`` and two operations every processor overrides."""

    document_name: str

    def supports_type(self) -> DocumentType:
        """Return the DocumentType this processor handles."""
        pass

    def process_document(self) -> None:
        """Print one line that describes the processing and includes the document name."""
        pass


@dataclass
class PresentationDocumentProcessor(DocumentProcessor):
    """Handles DocumentType.PRESENTATION; also offers ``add_slide()`` (prints a line)."""

    def supports_type(self) -> DocumentType:
        raise NotImplementedError("Implement PresentationDocumentProcessor.supports_type")

    def process_document(self):
        raise NotImplementedError("Implement PresentationDocumentProcessor.process_document")

    def add_slide(self):
        raise NotImplementedError("Implement add_slide")


@dataclass
class SpreadsheetDocumentProcessor(DocumentProcessor):
    """Handles DocumentType.SPREADSHEET; also offers ``perform_data_analysis()`` (prints a line)."""

    def supports_type(self) -> DocumentType:
        raise NotImplementedError("Implement SpreadsheetDocumentProcessor.supports_type")

    def process_document(self):
        raise NotImplementedError("Implement SpreadsheetDocumentProcessor.process_document")

    def perform_data_analysis(self):
        raise NotImplementedError("Implement perform_data_analysis")


@dataclass
class TextDocumentProcessor(DocumentProcessor):
    """Handles DocumentType.TEXT."""

    def supports_type(self) -> DocumentType:
        raise NotImplementedError("Implement TextDocumentProcessor.supports_type")

    def process_document(self):
        raise NotImplementedError("Implement TextDocumentProcessor.process_document")
