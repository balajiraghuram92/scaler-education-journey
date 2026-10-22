import json
import operator

import pytest

from workflow import END, Graph, Ledger


def build(store=None, ledger=None, crash_once=False):
    ledger = ledger if ledger is not None else Ledger()
    crashed = {"done": not crash_once}
    g = Graph(reducers={"log": operator.add}, store=store)

    g.add_node("classify", lambda s: {"kind": "refund" if "refund" in s["text"] else "other", "log": ["classify"]})
    g.add_node("draft", lambda s: {"amount": 20, "log": ["draft"]})

    def charge(s):
        key = f"{s['ticket']}:charge"
        receipt = ledger.run_once(key, lambda: f"receipt-{s['amount']}")
        if not crashed["done"]:
            crashed["done"] = True
            raise RuntimeError("process died after the effect, before the checkpoint")
        return {"receipt": receipt, "log": ["charge"]}

    g.add_node("charge", charge)
    g.add_node("reply", lambda s: {"log": ["reply"]})
    g.add_conditional_edges("classify", lambda s: "draft" if s["kind"] == "refund" else "reply")
    g.add_edge("draft", "charge")
    g.add_edge("charge", "reply")
    g.add_edge("reply", END)
    return g, ledger


INITIAL = {"ticket": "T1", "text": "please refund me", "log": []}
GATE = frozenset({"charge"})


def test_reducers_append_and_other_keys_overwrite():
    g, _ = build()
    out = g.run("t", initial=dict(INITIAL), entry="classify")
    assert out.status == "done" and out.next_node is None
    assert out.state["log"] == ["classify", "draft", "charge", "reply"]
    assert out.state["receipt"] == "receipt-20"

    g2 = Graph(reducers={"log": operator.add})

    def sneaky(state):
        state["log"].append("mutated")
        return {"log": ["real"]}

    g2.add_node("a", sneaky)
    g2.add_edge("a", END)
    assert g2.run("t", initial={"log": []}, entry="a").state["log"] == ["real"], "nodes get a deep copy of the state"


def test_ledger_runs_each_effect_at_most_once():
    ledger = Ledger()
    calls = []

    def effect():
        calls.append(1)
        return "receipt"

    assert ledger.run_once("k", effect) == "receipt"
    assert ledger.run_once("k", effect) == "receipt"
    assert calls == [1] and len(ledger) == 1
    assert ledger.run_once("other", lambda: "x") == "x" and len(ledger) == 2


def test_conditional_edge_skips_the_refund_branch():
    g, ledger = build()
    out = g.run("t", initial={"ticket": "T2", "text": "where is my parcel", "log": []}, entry="classify")
    assert out.state["log"] == ["classify", "reply"] and len(ledger) == 0


def test_unknown_router_target_is_rejected():
    g = Graph()
    g.add_node("a", lambda s: {})
    g.add_conditional_edges("a", lambda s: "nowhere")
    with pytest.raises(ValueError, match="unknown node"):
        g.run("t", initial={}, entry="a")


def test_pause_then_resume_from_a_new_instance_sharing_only_the_store():
    store = {}
    g1, ledger = build(store)
    paused = g1.run("t", initial=dict(INITIAL), entry="classify", interrupt_before=GATE)
    assert (paused.status, paused.next_node) == ("paused", "charge")
    assert len(ledger) == 0 and json.loads(store["t"])["paused"] is True

    g2, _ = build(store, ledger)
    done = g2.run("t", update={"approved": True}, interrupt_before=GATE)
    assert done.status == "done" and done.state["approved"] is True
    assert done.state["log"] == ["classify", "draft", "charge", "reply"]


def test_crash_after_effect_retries_without_a_second_charge():
    store = {}
    g, ledger = build(store, crash_once=True)
    with pytest.raises(RuntimeError):
        g.run("t", initial=dict(INITIAL), entry="classify")
    assert json.loads(store["t"])["next"] == "charge"          # checkpoint points at the failed node
    assert len(ledger) == 1
    out = g.run("t")                                           # retry
    assert out.status == "done" and len(ledger) == 1
    assert out.state["log"].count("charge") == 1


def test_crash_after_approval_does_not_ask_for_approval_again():
    store = {}
    g, ledger = build(store, crash_once=True)
    g.run("t", initial=dict(INITIAL), entry="classify", interrupt_before=GATE)
    with pytest.raises(RuntimeError):
        g.run("t", update={"approved": True}, interrupt_before=GATE)
    out = g.run("t", interrupt_before=GATE)
    assert out.status == "done" and len(ledger) == 1


def test_finished_threads_return_immediately():
    g, _ = build()
    g.run("t", initial=dict(INITIAL), entry="classify")
    again = g.run("t")
    assert again.status == "done" and again.state["log"] == ["classify", "draft", "charge", "reply"]
    with pytest.raises(ValueError):
        g.run("fresh", initial={})  # a new thread needs an entry node


def test_cycles_hit_the_step_limit():
    g = Graph(max_steps=5)
    g.add_node("a", lambda s: {})
    g.add_node("b", lambda s: {})
    g.add_edge("a", "b")
    g.add_edge("b", "a")
    with pytest.raises(RuntimeError, match="step limit"):
        g.run("t", initial={}, entry="a")


def test_non_serialisable_state_is_rejected():
    g = Graph()
    g.add_node("a", lambda s: {"bad": {1, 2}})
    g.add_edge("a", END)
    with pytest.raises(TypeError):
        g.run("t", initial={}, entry="a")
