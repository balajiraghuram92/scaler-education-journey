from abc import ABC
from dataclasses import dataclass
from enum import Enum


class DocumentType(Enum):
    PRESENTATION = "Presentation"
    SPREADSHEET = "Spreadsheet"
    TEXT = "Text"


@dataclass
class DocumentProcessor(ABC):
    document_name: str

    def supports_type(self) -> DocumentType:
        pass

    def process_document(self) -> None:
        pass


@dataclass
class PresentationDocumentProcessor(DocumentProcessor):

    def supports_type(self) -> DocumentType:
        return DocumentType.PRESENTATION

    def process_document(self):
        print(f"Processing a presentation document: {self.document_name}")

    def add_slide(self):
        print("Adding a slide to the presentation.")


@dataclass
class SpreadsheetDocumentProcessor(DocumentProcessor):

    def supports_type(self) -> DocumentType:
        return DocumentType.SPREADSHEET

    def process_document(self):
        print(f"Processing a spreadsheet document: {self.document_name}")

    def perform_data_analysis(self):
        print("Performing data analysis on the spreadsheet.")


@dataclass
class TextDocumentProcessor(DocumentProcessor):

    def supports_type(self) -> DocumentType:
        return DocumentType.TEXT

    def process_document(self):
        print(f"Processing a text document: {self.document_name}")
