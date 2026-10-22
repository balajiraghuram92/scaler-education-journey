from .products import *


class DocumentFactory:
    _PROCESSORS = {
        DocumentType.PRESENTATION: PresentationDocumentProcessor,
        DocumentType.SPREADSHEET: SpreadsheetDocumentProcessor,
        DocumentType.TEXT: TextDocumentProcessor,
    }

    @staticmethod
    def create_document(type: DocumentType, document_name: str) -> DocumentProcessor:
        try:
            processor_cls = DocumentFactory._PROCESSORS[type]
        except (KeyError, TypeError):
            raise ValueError(f"Unsupported document type: {type!r}") from None
        return processor_cls(document_name)
