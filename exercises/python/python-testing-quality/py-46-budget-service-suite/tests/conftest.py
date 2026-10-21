import pytest

from budget import BudgetService, InMemoryUsageRepo


@pytest.fixture
def repo() -> InMemoryUsageRepo:
    return InMemoryUsageRepo()


@pytest.fixture
def service(repo: InMemoryUsageRepo) -> BudgetService:
    return BudgetService(repo, limit=1_000)
