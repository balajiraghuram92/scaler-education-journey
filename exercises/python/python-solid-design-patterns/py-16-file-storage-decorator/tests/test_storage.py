import pytest

from config.decorator import BaseFileDecorator, CompressionDecorator, VirusScanDecorator
from config.storage import FileStorage
from config.utils import StorageUtils


class MemoryStorage(FileStorage):
    def __init__(self):
        self.files = {}
        self.retrievals = 0

    def store_file(self, file_data, file_name):
        self.files[file_name] = file_data

    def retrieve_file(self, file_name):
        self.retrievals += 1
        return self.files[file_name]


@pytest.fixture
def utils(monkeypatch):
    """Make the helpers observable: compress prefixes, decompress strips it, scan records its input."""
    calls = {"scan": [], "compress": [], "decompress": []}

    def compress(data):
        calls["compress"].append(data)
        return b"Z:" + data

    def decompress(data):
        calls["decompress"].append(data)
        assert data.startswith(b"Z:"), "decompress received data that was never compressed"
        return data[2:]

    def scan(data):
        calls["scan"].append(data)
        return b"EICAR" not in data

    monkeypatch.setattr(StorageUtils, "compress", staticmethod(compress))
    monkeypatch.setattr(StorageUtils, "decompress", staticmethod(decompress))
    monkeypatch.setattr(StorageUtils, "scan_for_virus", staticmethod(scan))
    return calls


def test_base_decorator_is_a_file_storage_that_delegates():
    inner = MemoryStorage()
    deco = BaseFileDecorator(inner)
    assert issubclass(BaseFileDecorator, FileStorage), "BaseFileDecorator must inherit from FileStorage"
    assert deco._file_storage is inner, "keep the wrapped storage in _file_storage"
    deco.store_file(b"abc", "a.txt")
    assert inner.files == {"a.txt": b"abc"}, "store_file must delegate unchanged"
    assert deco.retrieve_file("a.txt") == b"abc", "retrieve_file must return the wrapped result"


def test_compression_stores_compressed_bytes(utils):
    inner = MemoryStorage()
    CompressionDecorator(inner).store_file(b"hello", "h.txt")
    assert inner.files["h.txt"] == b"Z:hello", "the wrapped storage must receive StorageUtils.compress(data)"
    assert utils["compress"] == [b"hello"]


def test_compression_decompresses_on_retrieve(utils):
    inner = MemoryStorage()
    inner.files["h.txt"] = b"Z:hello"
    assert CompressionDecorator(inner).retrieve_file("h.txt") == b"hello", "retrieve must return decompressed data"
    assert utils["decompress"] == [b"Z:hello"]


def test_compression_round_trip(utils):
    deco = CompressionDecorator(MemoryStorage())
    deco.store_file(b"payload", "p")
    assert deco.retrieve_file("p") == b"payload"


def test_virus_scan_allows_clean_files(utils):
    inner = MemoryStorage()
    VirusScanDecorator(inner).store_file(b"clean", "c.txt")
    assert inner.files == {"c.txt": b"clean"}
    assert utils["scan"] == [b"clean"], "the scanner must be called once with the file data"


def test_virus_scan_rejects_infected_files_and_stores_nothing(utils):
    inner = MemoryStorage()
    with pytest.raises(ValueError, match="File contains virus and cannot be stored"):
        VirusScanDecorator(inner).store_file(b"xxEICARxx", "bad.txt")
    assert inner.files == {}, "an infected file must not reach the wrapped storage"


def test_virus_scan_does_not_scan_on_retrieve(utils):
    inner = MemoryStorage()
    inner.files["f"] = b"data"
    assert VirusScanDecorator(inner).retrieve_file("f") == b"data"
    assert utils["scan"] == [], "retrieval must not call the scanner"


def test_decorators_stack_and_order_matters(utils):
    # Scan first, then compress: the scanner sees the raw bytes.
    inner = MemoryStorage()
    scan_then_compress = VirusScanDecorator(CompressionDecorator(inner))
    scan_then_compress.store_file(b"data", "a")
    assert utils["scan"] == [b"data"], "outer decorator runs first, so the scanner sees the raw data"
    assert inner.files["a"] == b"Z:data"
    assert scan_then_compress.retrieve_file("a") == b"data", "stacked decorators must round-trip"

    # Compress first, then scan: the scanner sees the compressed bytes.
    utils["scan"].clear()
    inner2 = MemoryStorage()
    CompressionDecorator(VirusScanDecorator(inner2)).store_file(b"data", "b")
    assert utils["scan"] == [b"Z:data"], "when compression is the outer layer the scanner sees compressed bytes"
    assert inner2.files["b"] == b"Z:data"


def test_decorators_are_interchangeable_with_plain_storage(utils):
    stack = VirusScanDecorator(CompressionDecorator(VirusScanDecorator(MemoryStorage())))
    assert isinstance(stack, FileStorage), "any stack of decorators is still a FileStorage"
    stack.store_file(b"x", "x")
    assert stack.retrieve_file("x") == b"x"
