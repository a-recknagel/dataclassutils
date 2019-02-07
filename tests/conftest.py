from pathlib import Path
from typing import Dict, List

import pytest


TESTS_ROOT_DIR = Path(__file__).parent
FIXTURES = TESTS_ROOT_DIR / 'fixtures'


def pytest_addoption(parser):
    """Add a custom option to pytest.

    Due to pytest limitations, this function needs to live at the top level
    conftest - even though it would fit in much better in a
    tests/functional/integration/conftest.py file.
    """
    parser.addoption('--integration', action='store_true', dest="integration",
                     default=False, help="enable integration tests")


def pytest_configure(config):
    """Ensure that integration tests run iff the --integration flag is present.

    Running `pytest` by itself does not invoke the integration tests. Similarly,
    running `pytest --integration` does not invoke the unit tests. This way, we
    can let them run as separate stages in the CI.
    """
    if config.option.integration:
        setattr(config.option, 'markexpr', 'integration')
    else:
        setattr(config.option, 'markexpr', 'not integration')


class Pepe:
    a: str


class TestNestedList:
    a: List[List[Pepe]]
    b: List[List[int]]


class TestNestedDict:
    a: Dict[str, List[Pepe]]
    b: Dict[str, List[int]]


@pytest.fixture
def fixture_pepe():
    return Pepe


@pytest.fixture
def fixture_nested_list():
    return TestNestedList


@pytest.fixture
def fixture_nested_dict():
    return TestNestedDict


@pytest.fixture
def fixture_decorated_validate_pepe(fixture_pepe):
    from c11h.dataclassutils.re_wrap import dataclass
    return dataclass(validate=True)(fixture_pepe)


@pytest.fixture
def fixture_decorated_invalid_pepe(fixture_pepe):
    from c11h.dataclassutils.re_wrap import dataclass
    return dataclass(fixture_pepe)
