import pytest

from c11h.dataclassutils.re_wrap import dataclass


@dataclass(ignore_additional_properties=True)
class SimpleTolerantClass:
    a: int


@dataclass
class SimpleIntolerantClass:
    a: int


def test_tolerant_normal_initialization():
    assert SimpleTolerantClass(**{'a': 1})


def test_tolerant_additional_initialization():
    assert SimpleTolerantClass(**{'a': 1, 'b': 2})


def test_tolerant_empty_initialization():
    with pytest.raises(TypeError):
        SimpleTolerantClass(**{})


def test_intolerant_empty_initialization():
    with pytest.raises(TypeError):
        SimpleIntolerantClass(**{})


def test_intolerant():
    assert SimpleIntolerantClass(**{'a': 1})


def test_aditional_field():
    with pytest.raises(TypeError):
        SimpleIntolerantClass(**{'a': 1, 'b': 2})
