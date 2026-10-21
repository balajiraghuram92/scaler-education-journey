import dataclasses
import json

import pytest
from pydantic import ValidationError

from events import (
    ItemError,
    PaymentFailed,
    PaymentSucceeded,
    RefundIssued,
    WebhookSettings,
    parse_events,
    parse_events_lenient,
)

OK = {
    "type": "payment.succeeded",
    "id": "e1",
    "created": "2025-03-01T12:00:00Z",
    "amount_cents": 1999,
    "currency": "USD",
}
FAILED = {"type": "payment.failed", "id": "e3", "created": "2025-03-01T12:02:00Z", "reason": "declined"}
REFUND = {
    "type": "refund.issued",
    "id": "e6",
    "created": "2025-03-01T12:03:00Z",
    "amount_cents": 500,
    "original_event_id": "e1",
}
UNKNOWN = {"type": "payment.refunded", "id": "e2", "created": "2025-03-01T12:01:00Z"}
BAD_AMOUNT = {**OK, "id": "e4", "amount_cents": 0}
NO_TYPE = {"id": "e5", "created": "2025-03-01T12:01:00Z"}


def raw(*items: dict) -> bytes:
    return json.dumps(list(items)).encode()


@pytest.fixture
def secret_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    monkeypatch.setenv("WEBHOOK_SECRET", "whsec_test_secret")
    monkeypatch.delenv("WEBHOOK_TOLERANCE_S", raising=False)
    return monkeypatch


def test_valid_mixed_batch():
    events = parse_events(raw(OK, FAILED, REFUND))
    assert [type(e) for e in events] == [PaymentSucceeded, PaymentFailed, RefundIssued], "events must keep their order and type"
    assert events[0].amount_cents == 1999 and events[0].created.year == 2025
    assert parse_events(b"[]") == [], "an empty array is a valid batch"


def test_strict_failure_reports_index():
    with pytest.raises(ValidationError) as info:
        parse_events(raw(OK, UNKNOWN))
    assert info.value.errors()[0]["loc"][0] == 1, "the first error location must start with the bad item's index"
    with pytest.raises(ValidationError):
        parse_events(b'{"type": "payment.failed"}')


def test_lenient_returns_good_events_and_errors():
    good, errors = parse_events_lenient(raw(OK, UNKNOWN, FAILED, BAD_AMOUNT))
    assert [e.id for e in good] == ["e1", "e3"], "valid events must survive a bad neighbour"
    assert (errors[0].index, errors[0].type) == (1, "union_tag_invalid")
    assert {e.index for e in errors} == {1, 3}
    amount = next(e for e in errors if e.index == 3)
    assert amount.type == "greater_than" and amount.loc[-1] == "amount_cents"
    assert isinstance(amount.loc, tuple) and isinstance(amount.msg, str)


def test_missing_tag_and_non_array_payload():
    _, errors = parse_events_lenient(raw(NO_TYPE))
    assert errors[0].type == "union_tag_not_found"
    with pytest.raises(ValueError):
        parse_events_lenient(b'{"type": "payment.failed"}')
    good, errors = parse_events_lenient(raw(FAILED, 42, "oops"))
    assert len(good) == 1 and {e.index for e in errors} == {1, 2}, "non-object items are reported, not raised"


def test_event_field_constraints():
    for bad in (
        {**OK, "id": ""},
        {**OK, "currency": "GBP"},
        {**OK, "created": "not-a-date"},
        {**REFUND, "original_event_id": None},
        {k: v for k, v in FAILED.items() if k != "reason"},
    ):
        with pytest.raises(ValidationError):
            parse_events(raw(bad))


def test_events_and_item_errors_are_frozen():
    event = parse_events(raw(FAILED))[0]
    with pytest.raises(ValidationError):
        event.reason = "changed"  # type: ignore[misc]
    item = ItemError(index=0, type="x", loc=("a",), msg="m")
    with pytest.raises(dataclasses.FrozenInstanceError):
        item.index = 1  # type: ignore[misc]


def test_settings_from_environment(secret_env):
    secret_env.setenv("WEBHOOK_TOLERANCE_S", "120")
    settings = WebhookSettings(_env_file=None)
    assert settings.secret.get_secret_value() == "whsec_test_secret"
    assert settings.tolerance_s == 120
    assert "whsec_test_secret" not in repr(settings), "the secret must never appear in repr/logs"
    assert "whsec_test_secret" not in str(settings)


def test_missing_or_short_secret_fails_fast(monkeypatch):
    monkeypatch.delenv("WEBHOOK_SECRET", raising=False)
    with pytest.raises(ValidationError):
        WebhookSettings(_env_file=None)
    monkeypatch.setenv("WEBHOOK_SECRET", "short")
    with pytest.raises(ValidationError):
        WebhookSettings(_env_file=None)
    monkeypatch.setenv("WEBHOOK_SECRET", "12345678")
    assert WebhookSettings(_env_file=None).secret.get_secret_value() == "12345678", "8 characters is enough"


def test_tolerance_default_and_bounds(secret_env):
    assert WebhookSettings(_env_file=None).tolerance_s == 300, "default tolerance is 300 seconds"
    for bad in ("abc", "0", "-5", "3601"):
        secret_env.setenv("WEBHOOK_TOLERANCE_S", bad)
        with pytest.raises(ValidationError):
            WebhookSettings(_env_file=None)
    secret_env.setenv("WEBHOOK_TOLERANCE_S", "3600")
    assert WebhookSettings(_env_file=None).tolerance_s == 3600


def test_env_file_is_read_and_unknown_keys_ignored(monkeypatch, tmp_path):
    monkeypatch.delenv("WEBHOOK_SECRET", raising=False)
    monkeypatch.delenv("WEBHOOK_TOLERANCE_S", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("WEBHOOK_SECRET=from_dotenv_file\nWEBHOOK_TOLERANCE_S=60\nUNRELATED=1\nWEBHOOK_UNKNOWN=2\n")
    settings = WebhookSettings(_env_file=str(env_file))
    assert settings.secret.get_secret_value() == "from_dotenv_file"
    assert settings.tolerance_s == 60
