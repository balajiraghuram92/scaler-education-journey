import pytest

from config.abstract_factory import DocumentFactory, SpreadsheetDocumentFactory, TextDocumentFactory
from config.document_parser import DocumentParser, SpreadsheetDocumentParser, TextDocumentParser
from config.printer import DocumentPrinter, SpreadsheetDocumentPrinter, TextDocumentPrinter
from config.processor import DocumentProcessor, DocumentType, SpreadsheetDocumentProcessor, TextDocumentProcessor

FAMILIES = [
    (TextDocumentFactory, DocumentType.TEXT, TextDocumentProcessor, TextDocumentParser, TextDocumentPrinter),
    (SpreadsheetDocumentFactory, DocumentType.SPREAD_SHEET, SpreadsheetDocumentProcessor, SpreadsheetDocumentParser, SpreadsheetDocumentPrinter),
]
IDS = ["text", "spreadsheet"]


def test_document_factory_is_abstract_with_four_abstract_methods():
    with pytest.raises(TypeError):
        DocumentFactory()
    assert DocumentFactory.__abstractmethods__ == {
        "create_processor",
        "create_parser",
        "create_printer",
        "supports_type",
    }, f"abstract methods found: {sorted(DocumentFactory.__abstractmethods__)}"


@pytest.mark.parametrize("factory_cls, doc_type, processor, parser, printer", FAMILIES, ids=IDS)
def test_concrete_factories_are_instantiable_and_report_their_type(factory_cls, doc_type, processor, parser, printer):
    assert issubclass(factory_cls, DocumentFactory)
    assert factory_cls().supports_type() is doc_type


@pytest.mark.parametrize("factory_cls, doc_type, processor, parser, printer", FAMILIES, ids=IDS)
def test_factory_creates_the_concrete_products_of_its_family(factory_cls, doc_type, processor, parser, printer):
    factory = factory_cls()
    made_processor = factory.create_processor("report")
    assert type(made_processor) is processor
    assert type(factory.create_parser("/tmp/report")) is parser
    assert type(factory.create_printer(made_processor)) is printer


@pytest.mark.parametrize("factory_cls, doc_type, processor, parser, printer", FAMILIES, ids=IDS)
def test_products_share_the_common_abstract_parents(factory_cls, doc_type, processor, parser, printer):
    factory = factory_cls()
    made_processor = factory.create_processor("report")
    assert isinstance(made_processor, DocumentProcessor)
    assert isinstance(factory.create_parser("p"), DocumentParser)
    assert isinstance(factory.create_printer(made_processor), DocumentPrinter)


@pytest.mark.parametrize("factory_cls, doc_type, processor, parser, printer", FAMILIES, ids=IDS)
def test_every_product_matches_the_factorys_type(factory_cls, doc_type, processor, parser, printer):
    factory = factory_cls()
    made_processor = factory.create_processor("report")
    products = [made_processor, factory.create_parser("p"), factory.create_printer(made_processor)]
    assert [p.supports_type() for p in products] == [doc_type] * 3, "all three products must come from the same family"


def test_arguments_reach_the_products_and_printer_wraps_the_processor():
    factory = TextDocumentFactory()
    made_processor = factory.create_processor("notes")
    parser = factory.create_parser("/data/notes.txt")
    printer = factory.create_printer(made_processor)
    assert made_processor.document_name == "notes"
    assert parser.path == "/data/notes.txt"
    assert printer.processor is made_processor, "the factory must pass the processor through to the printer"


def test_each_call_creates_a_new_product():
    factory = SpreadsheetDocumentFactory()
    assert factory.create_processor("a") is not factory.create_processor("a")
    assert factory.create_parser("p") is not factory.create_parser("p")


def test_client_code_depends_only_on_the_abstract_factory():
    def run(factory: DocumentFactory):
        processor = factory.create_processor("doc")
        return {
            processor.supports_type(),
            factory.create_parser("path").supports_type(),
            factory.create_printer(processor).supports_type(),
        }

    for factory_cls, doc_type, *_ in FAMILIES:
        assert run(factory_cls()) == {doc_type}, "one factory must never mix document types"
