import pytest

from ecom.adapters.email_adapter import EmailAdapter
from ecom.adapters.email_adapter_impl import EmailAdapterImpl
from ecom.controllers.inventory_controller import InventoryController
from ecom.controllers.notification_controller import NotificationController
from ecom.dtos import (
    CreateUpdateInventoryReqDto,
    RegisterUserNotifyReqDto,
    ResponseStatus,
    UnregisterUserNotifyReqDto,
)
from ecom.exceptions import (
    NotificationNotFoundError,
    ProductInStockError,
    ProductNotFoundError,
    UserNotFoundError,
)
from ecom.libs import sendgrid
from ecom.models import Inventory, Notification, NotificationStatus, Product, User
from ecom.services.email_service import EmailService
from ecom.services.email_service_impl import EmailServiceImpl
from ecom.services.inventory_service_impl import InventoryServiceImpl
from ecom.services.notification_service_impl import NotificationServiceImpl
from ecom.store import Store


class RecordingEmailService(EmailService):
    def __init__(self):
        self.sent = []

    def notify_user(self, user, product):
        self.sent.append((user.name, product.name))
        return True


class RecordingAdapter(EmailAdapter):
    def __init__(self, result=True):
        self.emails = []
        self.result = result

    def send_email(self, to, subject, body):
        self.emails.append((to, subject, body))
        return self.result


class World:
    def __init__(self):
        self.store = Store()
        self.asha = self.store.add(User("Asha", "asha@example.com"))
        self.ravi = self.store.add(User("Ravi", "ravi@example.com"))
        self.phone = self.store.add(Product("Phone"))
        self.case = self.store.add(Product("Case"))
        self.new = self.store.add(Product("Brand New"))  # no inventory row yet
        self.store.add(Inventory(self.phone, 0))
        self.store.add(Inventory(self.case, 0))
        self.emails = RecordingEmailService()
        self.notifications = NotificationServiceImpl(self.store)
        self.inventory = InventoryServiceImpl(self.store, self.emails)


def test_register_creates_pending_notification():
    w = World()
    n = w.notifications.register_user(w.asha.id, w.phone.id)
    assert isinstance(n, Notification) and n.id
    assert n.user is w.asha and n.product is w.phone and n.status is NotificationStatus.PENDING
    assert w.store.find(Notification) == [n]


def test_register_validation():
    w = World()
    with pytest.raises(UserNotFoundError):
        w.notifications.register_user(999, w.phone.id)
    with pytest.raises(ProductNotFoundError):
        w.notifications.register_user(w.asha.id, w.new.id)
    w.store.inventory_of(w.phone.id).quantity = 3
    with pytest.raises(ProductInStockError):
        w.notifications.register_user(w.asha.id, w.phone.id)
    assert w.store.find(Notification) == []


def test_reregistering_resets_to_pending_without_duplicate():
    w = World()
    first = w.notifications.register_user(w.asha.id, w.phone.id)
    first.status = NotificationStatus.SENT
    again = w.notifications.register_user(w.asha.id, w.phone.id)
    assert again is first and again.status is NotificationStatus.PENDING
    assert len(w.store.find(Notification)) == 1


def test_unregister_deletes_or_raises():
    w = World()
    w.notifications.register_user(w.asha.id, w.phone.id)
    w.notifications.register_user(w.ravi.id, w.phone.id)
    w.notifications.unregister_user(w.asha.id, w.phone.id)
    assert [n.user.name for n in w.store.find(Notification)] == ["Ravi"]
    with pytest.raises(NotificationNotFoundError):
        w.notifications.unregister_user(w.asha.id, w.phone.id)
    with pytest.raises(NotificationNotFoundError):
        w.notifications.unregister_user(w.asha.id, w.case.id)


def test_restock_emails_pending_users_and_marks_sent():
    w = World()
    a = w.notifications.register_user(w.asha.id, w.phone.id)
    r = w.notifications.register_user(w.ravi.id, w.phone.id)
    inventory = w.inventory.save_or_update_inventory(w.phone.id, 25)
    assert inventory.quantity == 25 and w.store.inventory_of(w.phone.id).quantity == 25
    assert sorted(w.emails.sent) == [("Asha", "Phone"), ("Ravi", "Phone")]
    assert a.status is NotificationStatus.SENT and r.status is NotificationStatus.SENT


def test_restock_ignores_other_products_and_sent_notifications():
    w = World()
    on_phone = w.notifications.register_user(w.asha.id, w.phone.id)
    on_case = w.notifications.register_user(w.asha.id, w.case.id)
    already = w.notifications.register_user(w.ravi.id, w.phone.id)
    already.status = NotificationStatus.SENT
    w.inventory.save_or_update_inventory(w.phone.id, 5)
    assert w.emails.sent == [("Asha", "Phone")]
    assert on_phone.status is NotificationStatus.SENT
    assert on_case.status is NotificationStatus.PENDING, "other products stay pending"
    w.inventory.save_or_update_inventory(w.phone.id, 6)
    assert w.emails.sent == [("Asha", "Phone")], "a SENT notification is never emailed again"


def test_restock_creates_missing_inventory_and_rejects_unknown_product():
    w = World()
    created = w.inventory.save_or_update_inventory(w.new.id, 4)
    assert created.product is w.new and created.quantity == 4
    assert w.store.inventory_of(w.new.id) is created
    with pytest.raises(ProductNotFoundError):
        w.inventory.save_or_update_inventory(999, 4)
    assert w.emails.sent == []


def test_email_service_builds_subject_and_body():
    adapter = RecordingAdapter(result=True)
    user = User("Asha", "asha@example.com")
    product = Product("Phone X")
    assert EmailServiceImpl(adapter).notify_user(user, product) is True
    assert len(adapter.emails) == 1
    to, subject, body = adapter.emails[0]
    assert to == "asha@example.com"
    assert "Phone X" in subject and "Phone X" in body
    assert "Asha" in body, "address the user by name"
    assert EmailServiceImpl(RecordingAdapter(result=False)).notify_user(user, product) is False


def test_email_adapter_delegates_to_sendgrid(monkeypatch):
    calls = []

    def fake_send(to, subject, body):
        calls.append((to, subject, body))
        return False

    monkeypatch.setattr(sendgrid, "send_email", fake_send)
    adapter = EmailAdapterImpl()
    assert isinstance(adapter, EmailAdapter)
    assert adapter.send_email("a@b.c", "subj", "text") is False
    assert calls == [("a@b.c", "subj", "text")]


def test_controllers_translate_results():
    w = World()
    notify = NotificationController(w.notifications)
    ok = notify.register_user(RegisterUserNotifyReqDto(w.asha.id, w.phone.id))
    assert ok.response_status is ResponseStatus.SUCCESS and ok.notification_id == w.store.find(Notification)[0].id
    bad = notify.register_user(RegisterUserNotifyReqDto(999, w.phone.id))
    assert bad.response_status is ResponseStatus.FAILURE and bad.notification_id is None
    assert notify.unregister_user(UnregisterUserNotifyReqDto(w.asha.id, w.phone.id)).response_status \
        is ResponseStatus.SUCCESS
    assert notify.unregister_user(UnregisterUserNotifyReqDto(w.asha.id, w.phone.id)).response_status \
        is ResponseStatus.FAILURE
    stock = InventoryController(w.inventory)
    done = stock.create_or_update_inventory(CreateUpdateInventoryReqDto(product_id=w.phone.id, quantity=9))
    assert done.response_status is ResponseStatus.SUCCESS and done.inventory.quantity == 9
    missing = stock.create_or_update_inventory(CreateUpdateInventoryReqDto(product_id=999, quantity=9))
    assert missing.response_status is ResponseStatus.FAILURE
