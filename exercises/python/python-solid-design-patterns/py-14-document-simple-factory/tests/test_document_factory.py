import pytest

from document.factory import DocumentFactory
from document.products import (
    DocumentProcessor,
    DocumentType,
    PresentationDocumentProcessor,
    SpreadsheetDocumentProcessor,
    TextDocumentProcessor,
)

EXPECTED = {
    DocumentType.PRESENTATION: PresentationDocumentProcessor,
    DocumentType.SPREADSHEET: SpreadsheetDocumentProcessor,
    DocumentType.TEXT: TextDocumentProcessor,
}


@pytest.mark.parametrize("doc_type", list(DocumentType))
def test_factory_returns_the_right_concrete_type(doc_type):
    processor = DocumentFactory.create_document(doc_type, "report")
    assert type(processor) is EXPECTED[doc_type], f"{doc_type} should produce {EXPECTED[doc_type].__name__}"
    assert isinstance(processor, DocumentProcessor)
    assert processor.document_name == "report"
    assert processor.supports_type() is doc_type


def test_unknown_type_raises_value_error():
    with pytest.raises(ValueError):
        DocumentFactory.create_document("pdf", "report")
    with pytest.raises(ValueError):
        DocumentFactory.create_document(None, "report")


@pytest.mark.parametrize("doc_type", list(DocumentType))
def test_process_document_prints_a_line_with_the_name(capsys, doc_type):
    DocumentFactory.create_document(doc_type, "quarterly-plan").process_document()
    out = capsys.readouterr().out
    assert "quarterly-plan" in out, "process_document must mention the document name"
    assert len(out.strip().splitlines()) == 1, "print exactly one line"


def test_each_processor_describes_its_own_kind(capsys):
    outputs = {}
    for doc_type in DocumentType:
        DocumentFactory.create_document(doc_type, "d").process_document()
        outputs[doc_type] = capsys.readouterr().out.lower()
    assert "presentation" in outputs[DocumentType.PRESENTATION]
    assert "spreadsheet" in outputs[DocumentType.SPREADSHEET]
    assert "text" in outputs[DocumentType.TEXT]


def test_specialised_operations(capsys):
    sheet = DocumentFactory.create_document(DocumentType.SPREADSHEET, "s")
    deck = DocumentFactory.create_document(DocumentType.PRESENTATION, "p")
    sheet.perform_data_analysis()
    assert "analysis" in capsys.readouterr().out.lower()
    deck.add_slide()
    assert "slide" in capsys.readouterr().out.lower()
    assert not hasattr(DocumentFactory.create_document(DocumentType.TEXT, "t"), "add_slide")


def test_factory_returns_a_new_processor_each_call():
    a = DocumentFactory.create_document(DocumentType.TEXT, "a")
    b = DocumentFactory.create_document(DocumentType.TEXT, "b")
    assert a is not b and (a.document_name, b.document_name) == ("a", "b")


def test_factory_builds_only_the_selected_processor(monkeypatch):
    built = []
    for cls in EXPECTED.values():
        original = cls.__init__

        def tracking_init(self, *a, _orig=original, **k):
            built.append(type(self))
            _orig(self, *a, **k)

        monkeypatch.setattr(cls, "__init__", tracking_init)
    DocumentFactory.create_document(DocumentType.TEXT, "x")
    assert built == [TextDocumentProcessor], f"only the requested product may be constructed, built: {built}"


def test_every_document_type_is_handled_through_the_base_interface():
    for doc_type in DocumentType:
        processor = DocumentFactory.create_document(doc_type, "n")
        assert processor.supports_type() is doc_type
