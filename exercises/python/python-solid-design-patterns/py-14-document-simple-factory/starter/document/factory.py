from .products import *


class DocumentFactory:
    """Simple Factory: callers pass a DocumentType and never name a concrete processor."""

    @staticmethod
    def create_document(type: DocumentType, document_name: str) -> DocumentProcessor:
        """Return the processor for ``type`` built with ``document_name``.

        Construct ONLY the selected processor. An unsupported ``type`` raises ValueError.
        """
        raise NotImplementedError("Implement create_document")
