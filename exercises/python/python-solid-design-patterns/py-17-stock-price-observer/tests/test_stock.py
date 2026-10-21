import inspect

import pytest

from stock.manager import StockTradingManager
from stock.observer import AppService, EmailService, Observer, SmsService
from stock.publisher import Publisher
from stock.registry import ObserverRegistry


class Recorder(Observer):
    def __init__(self, name, log):
        self.name, self.log = name, log

    def send_notification(self, stock_name, current_price):
        self.log.append((self.name, stock_name, current_price))


def test_observer_interface_and_channel_services(capsys):
    assert inspect.isabstract(Observer), "Observer must be an ABC with an abstract method"
    assert "send_notification" in Observer.__abstractmethods__
    for cls, word in ((AppService, "app"), (EmailService, "email"), (SmsService, "sms")):
        assert issubclass(cls, Observer), f"{cls.__name__} must subclass Observer"
        cls().send_notification("ACME", 123.5)
        out = capsys.readouterr().out
        assert word in out.lower() and "ACME" in out and "123.5" in out, (
            f"{cls.__name__} should print a line mentioning the channel, the stock and the price; got {out!r}"
        )


def test_publisher_keeps_a_per_instance_observers_list():
    p1, p2 = Publisher(), Publisher()
    assert isinstance(p1, ObserverRegistry)
    assert p1.observers == [] and isinstance(p1.observers, list), "observers must be a list created in __init__"
    p1.add_observer(Recorder("a", []))
    assert p2.observers == [], "each publisher needs its own list"


def test_notify_reaches_every_observer_in_subscription_order():
    log = []
    pub = Publisher()
    for name in ("first", "second", "third"):
        pub.add_observer(Recorder(name, log))
    pub.notify_observers("ACME", 10.5)
    assert log == [("first", "ACME", 10.5), ("second", "ACME", 10.5), ("third", "ACME", 10.5)], (
        f"observers must be notified in subscription order with (stock_name, price); got {log}"
    )


def test_unsubscribed_observer_is_not_notified():
    log = []
    pub = Publisher()
    keep, drop = Recorder("keep", log), Recorder("drop", log)
    pub.add_observer(keep)
    pub.add_observer(drop)
    pub.remove_observer(drop)
    pub.notify_observers("ACME", 1.0)
    assert [e[0] for e in log] == ["keep"], f"removed observers must not be notified; got {log}"
    assert pub.observers == [keep]


def test_observers_can_subscribe_at_runtime():
    log = []
    mgr = StockTradingManager("ACME", 100.0, 105.0)
    mgr.update_stock_price(110.0)
    assert log == []
    late = Recorder("late", log)
    mgr.add_observer(late)
    mgr.update_stock_price(120.0)
    assert log == [("late", "ACME", 120.0)], "a late subscriber receives only later updates"


def test_manager_is_a_publisher_with_initial_state():
    mgr = StockTradingManager("ACME", 100.0, 105.0)
    assert isinstance(mgr, Publisher)
    assert (mgr.stock_name, mgr.current_price, mgr.notification_threshold) == ("ACME", 100.0, 105.0)
    assert mgr.observers == [], "super().__init__() must have created the observers list"


def test_notifies_only_when_price_is_strictly_above_threshold():
    log = []
    mgr = StockTradingManager("ACME", 100.0, 105.0)
    mgr.add_observer(Recorder("r", log))
    mgr.update_stock_price(104.0)
    mgr.update_stock_price(105.0)
    assert log == [], "no notification at or below the threshold"
    mgr.update_stock_price(105.01)
    assert log == [("r", "ACME", 105.01)], "notify with the stock name and the new price above the threshold"


def test_price_is_updated_even_when_nobody_is_notified():
    mgr = StockTradingManager("ACME", 100.0, 105.0)
    mgr.update_stock_price(90.0)
    assert mgr.current_price == 90.0, "current_price must always be updated"


def test_real_channels_work_through_the_manager(capsys):
    mgr = StockTradingManager("ACME", 100.0, 105.0)
    for svc in (AppService(), EmailService(), SmsService()):
        mgr.add_observer(svc)
    mgr.update_stock_price(150.0)
    lines = [l for l in capsys.readouterr().out.splitlines() if l.strip()]
    assert len(lines) == 3, f"expected one line per channel, got {lines}"
    assert [("app" in l.lower(), "email" in l.lower(), "sms" in l.lower()) for l in lines] == [
        (True, False, False), (False, True, False), (False, False, True)
    ], "channels must be notified in subscription order"
