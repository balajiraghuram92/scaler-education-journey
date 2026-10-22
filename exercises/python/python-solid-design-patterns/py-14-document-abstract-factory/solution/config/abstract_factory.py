from abc import ABC, abstractmethod

from .document_parser import DocumentParser, SpreadsheetDocumentParser, TextDocumentParser
from .printer import DocumentPrinter, SpreadsheetDocumentPrinter, TextDocumentPrinter
from .processor import DocumentProcessor, DocumentType, SpreadsheetDocumentProcessor, TextDocumentProcessor


class DocumentFactory(ABC):
    @abstractmethod
    def create_processor(self, document_name: str) -> DocumentProcessor:
        pass

    @abstractmethod
    def create_parser(self, path: str) -> DocumentParser:
        pass

    @abstractmethod
    def create_printer(self, processor: DocumentProcessor) -> DocumentPrinter:
        pass

    @abstractmethod
    def supports_type(self) -> DocumentType:
        pass


class TextDocumentFactory(DocumentFactory):
    def create_processor(self, document_name: str) -> DocumentProcessor:
        return TextDocumentProcessor(document_name)

    def create_parser(self, path: str) -> DocumentParser:
        return TextDocumentParser(path)

    def create_printer(self, processor: DocumentProcessor) -> DocumentPrinter:
        return TextDocumentPrinter(processor)

    def supports_type(self) -> DocumentType:
        return DocumentType.TEXT


class SpreadsheetDocumentFactory(DocumentFactory):
    def create_processor(self, document_name: str) -> DocumentProcessor:
        return SpreadsheetDocumentProcessor(document_name)

    def create_parser(self, path: str) -> DocumentParser:
        return SpreadsheetDocumentParser(path)

    def create_printer(self, processor: DocumentProcessor) -> DocumentPrinter:
        return SpreadsheetDocumentPrinter(processor)

    def supports_type(self) -> DocumentType:
        return DocumentType.SPREAD_SHEET
