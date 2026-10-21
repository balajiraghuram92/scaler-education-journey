import pytest

from invoice.cloneable import Cloneable
from invoice.invoice_model import Invoice, InvoiceType
from invoice.registry import InvoicePrototypeRegistry
from invoice.registry_impl import InvoicePrototypeRegistryImpl


@pytest.fixture
def registry():
    reg = InvoicePrototypeRegistryImpl()
    reg.add_prototype(Invoice(1, 'Acme', 100.0, 'card', InvoiceType.STANDARD))
    reg.add_prototype(Invoice(1, 'Acme', 100.0, 'card', InvoiceType.PRO_FORMA))
    return reg


def test_clone_object_returns_an_equal_but_distinct_object():
    original = Invoice(1, 'Acme', 100.0, 'card', InvoiceType.STANDARD)
    clone = original.clone_object()
    assert isinstance(clone, Invoice), "clone_object must return a Invoice"
    assert clone == original, "a clone has the same field values"
    assert clone is not original, "a clone must be a separate object"


def test_changing_a_clone_object_does_not_change_the_original():
    proto = Invoice(1, 'Acme', 100.0, 'card', InvoiceType.STANDARD)
    clone = proto.clone_object()
    clone.customer_name = 'Changed'
    clone.amount = 999.0
    assert proto.customer_name == 'Acme' and proto.amount == 100.0, "mutating the clone must not touch the original"


def test_registry_and_model_follow_the_prototype_interfaces():
    assert issubclass(Invoice, Cloneable), "Invoice must implement Cloneable"
    assert isinstance(InvoicePrototypeRegistryImpl(), InvoicePrototypeRegistry)


def test_get_prototype_returns_the_stored_prototype(registry):
    proto = registry.get_prototype(InvoiceType.STANDARD)
    assert proto == Invoice(1, 'Acme', 100.0, 'card', InvoiceType.STANDARD)
    assert registry.get_prototype(InvoiceType.STANDARD) is proto, "get_prototype returns the stored object, not a copy"
    assert registry.get_prototype(InvoiceType.PRO_FORMA) == Invoice(1, 'Acme', 100.0, 'card', InvoiceType.PRO_FORMA), "prototypes are keyed by type_"


def test_get_prototype_unknown_type_returns_none():
    assert InvoicePrototypeRegistryImpl().get_prototype(InvoiceType.STANDARD) is None


def test_clone_returns_a_copy_not_the_shared_prototype(registry):
    proto = registry.get_prototype(InvoiceType.STANDARD)
    first_clone = registry.clone(InvoiceType.STANDARD)
    second_clone = registry.clone(InvoiceType.STANDARD)
    assert first_clone == proto
    assert first_clone is not proto, "clone() must never hand out the stored prototype"
    assert first_clone is not second_clone, "every clone() call returns a new object"


def test_changing_a_registry_clone_does_not_change_the_stored_prototype(registry):
    clone = registry.clone(InvoiceType.STANDARD)
    clone.customer_name = 'Changed'
    clone.amount = 999.0
    proto = registry.get_prototype(InvoiceType.STANDARD)
    assert proto.customer_name == 'Acme' and proto.amount == 100.0, "the stored prototype must be unaffected by changes to a clone"
    assert registry.clone(InvoiceType.STANDARD) == Invoice(1, 'Acme', 100.0, 'card', InvoiceType.STANDARD), "later clones still start from the pristine prototype"


def test_clone_unknown_type_returns_none():
    reg = InvoicePrototypeRegistryImpl()
    reg.add_prototype(Invoice(1, 'Acme', 100.0, 'card', InvoiceType.STANDARD))
    assert reg.clone(InvoiceType.RECURRING) is None, "unknown type should give None"


def test_adding_a_prototype_of_an_existing_type_replaces_it():
    reg = InvoicePrototypeRegistryImpl()
    reg.add_prototype(Invoice(1, 'Acme', 100.0, 'card', InvoiceType.STANDARD))
    replacement = Invoice(1, 'Acme', 100.0, 'card', InvoiceType.STANDARD)
    replacement.customer_name = "replaced"
    reg.add_prototype(replacement)
    assert reg.get_prototype(InvoiceType.STANDARD) is replacement, "one prototype per type: the newest wins"
