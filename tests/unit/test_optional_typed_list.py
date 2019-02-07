from typing import List, Optional

import pytest

from c11h.dataclassutils import dataclass, field
from c11h.dataclassutils.util.exceptions import NestedInitializationException


@dataclass(nest=True, validate=True)
class A:
    a: int


@dataclass(nest=True, validate=True)
class B:
    b: Optional[List[A]]


@dataclass(nest=True, validate=True)
class C:
    b: List[A] = field(optional=True)


@pytest.fixture
def empty_data():
    return {}


@pytest.fixture
def valid_data():
    return {'b': [{'a': 1}, {'a': 2}, {'a': 3}]}


@pytest.fixture
def invalid_data():
    return {'b': [{'a': 1}, 2, {'a': '3'}]}


def test_initialization_optional(empty_data, valid_data, invalid_data):
    assert B(**empty_data)
    assert B(**valid_data)
    with pytest.raises(NestedInitializationException):
        B(**invalid_data)


def test_initialization_field(empty_data, valid_data, invalid_data):
    assert C(**empty_data)
    assert C(**valid_data)
    with pytest.raises(NestedInitializationException):
        C(**invalid_data)
