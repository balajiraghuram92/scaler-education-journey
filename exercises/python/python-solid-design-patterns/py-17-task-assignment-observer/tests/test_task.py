import inspect

from task.manager import TaskManager
from task.observer import AppService, EmailService, Observer, SlackService
from task.publisher import Publisher
from task.registry import ObserverRegistry


class Recorder(Observer):
    def __init__(self, name, log):
        self.name, self.log = name, log

    def send_notification(self, user_id, task_id):
        self.log.append((self.name, user_id, task_id))


def test_observer_interface_and_channel_services(capsys):
    assert inspect.isabstract(Observer), "Observer must be an ABC with an abstract method"
    assert "send_notification" in Observer.__abstractmethods__
    for cls, word in ((AppService, "app"), (EmailService, "email"), (SlackService, "slack")):
        assert issubclass(cls, Observer), f"{cls.__name__} must subclass Observer"
        cls().send_notification(1234, 5678)
        out = capsys.readouterr().out
        assert word in out.lower() and "1234" in out and "5678" in out, (
            f"{cls.__name__} should print a line mentioning the channel, the user and the task; got {out!r}"
        )


def test_publisher_keeps_a_per_instance_observers_list():
    p1, p2 = Publisher(), Publisher()
    assert isinstance(p1, ObserverRegistry)
    assert p1.observers == [] and isinstance(p1.observers, list), "observers must be a list created in __init__"
    p1.add_observer(Recorder("a", []))
    assert p2.observers == [], "each publisher needs its own list"


def test_task_manager_passes_user_first_then_task():
    log = []
    mgr = TaskManager()
    mgr.add_observer(Recorder("r", log))
    mgr.assign_task(task_id=11, user_id=22)
    assert log == [("r", 22, 11)], f"observers receive (user_id, task_id); got {log}"


def test_every_observer_is_notified_in_subscription_order():
    log = []
    mgr = TaskManager()
    for name in ("app", "email", "slack"):
        mgr.add_observer(Recorder(name, log))
    mgr.assign_task(1, 2)
    assert [e[0] for e in log] == ["app", "email", "slack"], f"wrong notification order: {log}"
    assert all(e[1:] == (2, 1) for e in log)


def test_unsubscribed_observer_is_not_notified():
    log = []
    mgr = TaskManager()
    keep, drop = Recorder("keep", log), Recorder("drop", log)
    mgr.add_observer(keep)
    mgr.add_observer(drop)
    mgr.remove_observer(drop)
    mgr.assign_task(1, 2)
    assert [e[0] for e in log] == ["keep"], f"removed observers must not be notified; got {log}"
    assert mgr.observers == [keep]


def test_observers_can_be_added_and_removed_between_assignments():
    log = []
    mgr = TaskManager()
    a = Recorder("a", log)
    mgr.assign_task(1, 1)
    assert log == [], "no observers, no notifications"
    mgr.add_observer(a)
    mgr.assign_task(2, 7)
    mgr.remove_observer(a)
    mgr.assign_task(3, 7)
    assert log == [("a", 7, 2)], f"only the assignment made while subscribed should be seen; got {log}"


def test_managers_do_not_share_observers():
    log = []
    m1, m2 = TaskManager(), TaskManager()
    m1.add_observer(Recorder("only-m1", log))
    m2.assign_task(1, 2)
    assert log == [], "observer lists must be per manager"
    assert isinstance(m1, Publisher)


def test_real_channels_work_through_the_manager(capsys):
    mgr = TaskManager()
    for svc in (AppService(), EmailService(), SlackService()):
        mgr.add_observer(svc)
    mgr.assign_task(5678, 1234)
    lines = [l for l in capsys.readouterr().out.splitlines() if l.strip()]
    assert len(lines) == 3, f"expected one line per channel, got {lines}"
    assert all("1234" in l and "5678" in l for l in lines)
    assert ["app" in lines[0].lower(), "email" in lines[1].lower(), "slack" in lines[2].lower()] == [True] * 3
