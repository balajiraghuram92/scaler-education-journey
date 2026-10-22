import pytest

from adapters.aws_cloud_adapter import AWSCloudAdapter
from adapters.cloud_adapter import CloudAdapter
from adapters.google_cloud_adapter import GoogleCloudAdapter
from controllers.cloud_controller import CloudController
from dtos.create_connection_request_dto import CreateConnectionRequestDto
from exceptions.exceptions import UserNotFoundException
from libraries.aws.aws_api import AWSApi
from libraries.aws.aws_connection_response import AWSConnectionResponse
from libraries.google.google_api import GoogleApi
from libraries.google.google_connection_response import GoogleConnectionResponse
from models.connection import Connection
from models.enums import ConnectionStatus, ResponseStatus
from models.user import User
from repositories.user_repository_impl import UserRepositoryImpl
from services.cloud_service_impl import CloudServiceImpl


def aws_response(cid="aws-1", status="SUCCESS"):
    r = AWSConnectionResponse()
    r.connection_id, r.connection_status = cid, status
    return r


def google_response(cid="g-1", status="SUCCESS"):
    r = GoogleConnectionResponse()
    r.connection_id, r.connection_status = cid, status
    return r


@pytest.fixture
def patch_providers(monkeypatch):
    def apply(aws=None, google=None):
        calls = []
        if aws is not None:
            monkeypatch.setattr(AWSApi, "create_connection", lambda self, uid: calls.append(("aws", uid)) or aws)
        if google is not None:
            monkeypatch.setattr(GoogleApi, "create_connection", lambda self, uid: calls.append(("google", uid)) or google)
        return calls

    return apply


class FakeAdapter(CloudAdapter):
    def __init__(self):
        self.calls = []

    def create_connection(self, user_id):
        self.calls.append(user_id)
        c = Connection()
        c.connection_id, c.user_id, c.connection_status = "fake", user_id, ConnectionStatus.SUCCESS
        return c


def repo_with_user():
    repo = UserRepositoryImpl()
    user = User()
    user.name = "asha"
    repo.save(user)
    return repo, user


def test_aws_adapter_maps_provider_response(patch_providers):
    calls = patch_providers(aws=aws_response("abc-123"))
    conn = AWSCloudAdapter().create_connection(7)
    assert isinstance(conn, Connection)
    assert conn.connection_id == "abc-123"
    assert conn.user_id == 7
    assert conn.connection_status is ConnectionStatus.SUCCESS
    assert calls == [("aws", 7)], "the adapter must call the AWS SDK once with the user id"


def test_google_adapter_maps_provider_response(patch_providers):
    calls = patch_providers(google=google_response("goo-9"))
    conn = GoogleCloudAdapter().create_connection(3)
    assert isinstance(conn, Connection)
    assert (conn.connection_id, conn.user_id) == ("goo-9", 3)
    assert conn.connection_status is ConnectionStatus.SUCCESS
    assert calls == [("google", 3)]


@pytest.mark.parametrize("status", ["FAILED", "FAILURE", "", "success"])
def test_non_success_status_maps_to_failure(patch_providers, status):
    patch_providers(aws=aws_response(status=status), google=google_response(status=status))
    assert AWSCloudAdapter().create_connection(1).connection_status is ConnectionStatus.FAILURE
    assert GoogleCloudAdapter().create_connection(1).connection_status is ConnectionStatus.FAILURE


def test_adapters_implement_the_interface():
    assert issubclass(AWSCloudAdapter, CloudAdapter)
    assert issubclass(GoogleCloudAdapter, CloudAdapter)
    with pytest.raises(TypeError):
        CloudAdapter()


def test_service_rejects_unknown_user_without_calling_provider():
    repo, _ = repo_with_user()
    adapter = FakeAdapter()
    service = CloudServiceImpl(adapter, repo)
    with pytest.raises(UserNotFoundException, match="User not found"):
        service.create_connection(999)
    assert adapter.calls == [], "validate the user before touching the provider"


def test_service_delegates_to_injected_adapter():
    repo, user = repo_with_user()
    adapter = FakeAdapter()
    conn = CloudServiceImpl(adapter, repo).create_connection(user.id)
    assert adapter.calls == [user.id]
    assert conn.connection_id == "fake"


def test_controller_success_response():
    repo, user = repo_with_user()
    controller = CloudController(CloudServiceImpl(FakeAdapter(), repo))
    req = CreateConnectionRequestDto()
    req.user_id = user.id
    res = controller.create_connection(req)
    assert res.response_status is ResponseStatus.SUCCESS
    assert res.connection_id == "fake"
    assert res.connection_status is ConnectionStatus.SUCCESS


def test_controller_failure_response():
    repo, _ = repo_with_user()
    controller = CloudController(CloudServiceImpl(FakeAdapter(), repo))
    req = CreateConnectionRequestDto()
    req.user_id = 404
    res = controller.create_connection(req)
    assert res.response_status is ResponseStatus.FAILURE
    assert res.connection_id is None


def test_controller_does_not_swallow_other_errors():
    class Boom:
        def create_connection(self, user_id):
            raise RuntimeError("provider exploded")

    req = CreateConnectionRequestDto()
    req.user_id = 1
    with pytest.raises(RuntimeError):
        CloudController(Boom()).create_connection(req)


def test_provider_is_a_wiring_decision(patch_providers):
    patch_providers(aws=aws_response("A"), google=google_response("G"))
    repo, user = repo_with_user()
    from_aws = CloudServiceImpl(AWSCloudAdapter(), repo).create_connection(user.id)
    from_google = CloudServiceImpl(GoogleCloudAdapter(), repo).create_connection(user.id)
    assert (from_aws.connection_id, from_google.connection_id) == ("A", "G")
