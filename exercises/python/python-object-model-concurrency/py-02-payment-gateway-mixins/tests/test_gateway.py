import pytest

from audit_protocol import Auditable
from gateway import (
    PaymentGateway,
    PaytmGateway,
    PhonePeGateway,
    RazorpayGateway,
    run_audit_check,
)
from mixins import AuditMixin, LoggingMixin

GATEWAYS = [("phonepe", PhonePeGateway), ("razorpay", RazorpayGateway), ("paytm", PaytmGateway)]


@pytest.fixture
def clean_registry():
    before = dict(PaymentGateway.registry)
    yield PaymentGateway.registry
    PaymentGateway.registry.clear()
    PaymentGateway.registry.update(before)


def test_logging_mixin_prints_class_name_and_action(capsys):
    class Thing(LoggingMixin):
        pass

    Thing().log_action("hello")
    assert capsys.readouterr().out == "[LOG] Thing: hello\n", "format is [LOG] ClassName: action"


def test_audit_mixin_keeps_a_separate_trail_per_instance():
    class Audited(AuditMixin):
        pass

    a, b = Audited(), Audited()
    assert a.audit_trail == [], "the trail starts empty"
    a.record_audit("x")
    a.record_audit("y")
    assert a.audit_trail == ["x", "y"] and b.audit_trail == [], "the trail must not be shared between instances"


def test_audit_mixin_continues_the_cooperative_chain():
    seen = []

    class Next:
        def __init__(self, **kwargs):
            seen.append(kwargs)
            super().__init__()

    class Audited(AuditMixin, Next):
        pass

    obj = Audited(flag=True)
    assert seen == [{"flag": True}], "AuditMixin.__init__ must call super().__init__(**kwargs)"
    assert obj.audit_trail == []


def test_gateways_register_by_name():
    for name, cls in GATEWAYS:
        assert PaymentGateway.registry.get(name) is cls, f"{cls.__name__} must register as {name!r}"


def test_phonepe_worked_example(capsys):
    gateway = PaymentGateway.registry["phonepe"]()
    gateway.process_payment(500)
    assert capsys.readouterr().out == "[LOG] PhonePeGateway: Processing payment of 500\n"
    gateway.refund(200)
    out = capsys.readouterr().out
    assert out.startswith("[LOG] PhonePeGateway: ") and "200" in out, f"refund must log through log_action, got {out!r}"
    assert gateway.audit_trail == ["Processed payment of 500", "Refunded 200"]


@pytest.mark.parametrize("name, cls", GATEWAYS)
def test_every_gateway_logs_and_audits_both_operations(capsys, name, cls):
    gateway = cls()
    gateway.process_payment(10)
    gateway.refund(4)
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 2 and all(line.startswith(f"[LOG] {cls.__name__}: ") for line in lines), lines
    assert gateway.audit_trail == ["Processed payment of 10", "Refunded 4"]
    assert issubclass(cls, (PaymentGateway, LoggingMixin, AuditMixin)), "gateways combine the ABC and both mixins"


def test_abstract_contract_is_enforced(clean_registry):
    with pytest.raises(TypeError):
        PaymentGateway()

    class NoRefund(PaymentGateway, gateway_name="no-refund"):
        def process_payment(self, amount):
            pass

    with pytest.raises(TypeError):
        NoRefund()


def test_gateway_without_name_is_not_registered(clean_registry):
    size = len(clean_registry)

    class Internal(PaymentGateway):
        def process_payment(self, amount):
            pass

        def refund(self, amount):
            pass

    assert len(clean_registry) == size, "only named gateways are registered"


def test_auditable_protocol_accepts_gateways_and_foreign_classes():
    class VendorLedger:  # outside the hierarchy
        def record_audit(self, event):
            pass

    assert run_audit_check(PhonePeGateway()) is True
    assert run_audit_check(VendorLedger()) is True, "any object with record_audit is auditable"
    assert run_audit_check(object()) is False
    assert run_audit_check("not auditable") is False
    assert isinstance(VendorLedger(), Auditable), "Auditable must be @runtime_checkable"
