from abc import ABC, abstractmethod

from .document_parser import DocumentParser, SpreadsheetDocumentParser, TextDocumentParser
from .printer import DocumentPrinter, SpreadsheetDocumentPrinter, TextDocumentPrinter
from .processor import DocumentProcessor, DocumentType, SpreadsheetDocumentProcessor, TextDocumentProcessor


class DocumentFactory(ABC):
    """Abstract Factory for one document family.

    Declare FOUR abstract methods (so DocumentFactory cannot be instantiated):
      create_processor(document_name) -> DocumentProcessor
      create_parser(path) -> DocumentParser
      create_printer(processor) -> DocumentPrinter   (the printer is built FROM the processor)
      supports_type() -> DocumentType
    """


class TextDocumentFactory(DocumentFactory):
    """Implement all four methods; create only text products; supports_type() is DocumentType.TEXT."""


class SpreadsheetDocumentFactory(DocumentFactory):
    """Implement all four methods; create only spreadsheet products;
    supports_type() is DocumentType.SPREAD_SHEET."""
