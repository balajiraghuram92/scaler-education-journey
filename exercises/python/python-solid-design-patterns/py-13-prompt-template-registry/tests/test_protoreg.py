import copy
import threading

import pytest

from protoreg import HttpClient, PromptTemplate, Provider, TemplateRegistry


def make_template(client: HttpClient, name: str = "welcome") -> PromptTemplate:
    return PromptTemplate(name, "Be terse.", ["Q: hi"], client)


@pytest.fixture
def clean_providers():
    snapshot = dict(Provider.registry)
    yield
    Provider.registry.clear()
    Provider.registry.update(snapshot)


def test_clone_is_independent_but_shares_the_client():
    client = HttpClient()
    original = make_template(client)
    clone = copy.deepcopy(original)
    clone.examples.append("Q: bye")
    clone.system = "changed"
    assert original.examples == ["Q: hi"] and original.system == "Be terse.", "mutable data must be cloned"
    assert clone.client is original.client, "the expensive client must be shared, not copied"
    assert clone.name == "welcome" and clone is not original


def test_plain_deepcopy_of_the_client_fails():
    with pytest.raises(TypeError):
        copy.deepcopy(HttpClient())


def test_memo_handles_cycles_and_preserves_sharing():
    client = HttpClient()
    a, b = make_template(client, "a"), make_template(client, "b")
    a.parent, b.parent = b, a
    a2 = copy.deepcopy(a)
    assert a2.parent is not b, "the parent must be cloned too"
    assert a2.parent.parent is a2, "the cycle must be rebuilt through the memo"
    assert a2.client is client and a2.parent.client is client


def test_memo_keeps_shared_references_shared():
    client = HttpClient()
    shared_parent = make_template(client, "parent")
    c1, c2 = make_template(client, "c1"), make_template(client, "c2")
    c1.parent = c2.parent = shared_parent
    copies = copy.deepcopy([c1, c2])
    assert copies[0].parent is copies[1].parent, "one parent object copied once, thanks to the shared memo"


def test_get_returns_a_fresh_clone_every_time():
    registry = TemplateRegistry()
    registry.register(make_template(HttpClient()))
    first = registry.get("welcome")
    first.examples.append("leaked?")
    first.system = "changed"
    second = registry.get("welcome")
    assert second.examples == ["Q: hi"] and second.system == "Be terse."
    assert first is not second


def test_registry_keeps_a_private_copy_of_what_was_registered():
    registry = TemplateRegistry()
    client = HttpClient()
    template = make_template(client)
    registry.register(template)
    template.examples.append("mutated after register")
    got = registry.get("welcome")
    assert got.examples == ["Q: hi"], "register must store its own copy"
    assert got.client is client, "but the client is still shared"


def test_unknown_name_raises_with_known_names_and_names_are_sorted():
    registry = TemplateRegistry()
    client = HttpClient()
    registry.register(make_template(client, "welcome"))
    registry.register(make_template(client, "alpha"))
    with pytest.raises(KeyError, match="welcom'"):
        registry.get("welcom")
    with pytest.raises(KeyError, match="alpha"):
        registry.get("nope")
    assert registry.names() == ["alpha", "welcome"]


def test_duplicate_name_is_rejected():
    registry = TemplateRegistry()
    registry.register(make_template(HttpClient()))
    with pytest.raises(KeyError):
        registry.register(make_template(HttpClient()))


def test_duplicate_registration_from_many_threads_succeeds_exactly_once():
    registry = TemplateRegistry()
    client = HttpClient()
    barrier = threading.Barrier(8)
    outcomes = []
    out_lock = threading.Lock()

    def worker():
        barrier.wait(timeout=5)
        try:
            registry.register(make_template(client))
            result = "ok"
        except KeyError:
            result = "dup"
        with out_lock:
            outcomes.append(result)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    assert outcomes.count("ok") == 1 and outcomes.count("dup") == 7, f"got {outcomes}"


def test_providers_register_on_subclassing_and_reject_duplicates(clean_providers):
    class OpenAIProvider(Provider, name="test-openai"):
        def __init__(self, model: str = "m") -> None:
            self.model = model

    class LocalProvider(Provider):
        pass

    assert Provider.registry["test-openai"] is OpenAIProvider
    assert Provider.registry["local"] is LocalProvider, "default key: class name minus 'Provider', lower-cased"
    assert Provider.create("test-openai", model="x").model == "x"
    assert isinstance(Provider.create("local"), LocalProvider)
    with pytest.raises(TypeError, match="duplicate"):

        class Again(Provider, name="test-openai"):
            pass

    with pytest.raises(KeyError, match="known"):
        Provider.create("nope")
