from typing import List, Union

import pytest
from tests.unit.util.exceptions import PostInitException
from tests.unit.util.validator_functions import is_greater_0, is_odd

from c11h.dataclassutils.re_wrap import dataclass, field
from c11h.dataclassutils.util.exceptions import NestedInitializationException


@dataclass(validate=True)
class EvilPepe:
    a: str

    def __post_init__(self):
        raise PostInitException


@dataclass
class DecoratorNoParams:
    a: int


@dataclass(validate=True)
class AnnotatedList:
    a: List[int]


@dataclass(validate=True)
class DecoratorParams:
    a: int


@dataclass(validate=True)
class ErrorLists:
    a: List[List[int]]


@dataclass(nest=True, validate=True)
class UsesValidator:
    a: int = field(validators=is_greater_0)


@dataclass(nest=True, validate=True)
class UsesValidators:
    a: int = field(validators=[is_greater_0, is_odd])


@dataclass(nest=True, validate=True)
class NestedUsesValidator:
    a: UsesValidator
    b: UsesValidators


@dataclass(validate=True)
class UnitedPepe:
    a: Union[int, List]


def test_decorator_flags():
    assert DecoratorNoParams('I dont care about your type')
    with pytest.raises(NestedInitializationException):
        DecoratorParams('I care about your type')


def test_valid_invalid_pepe(fixture_decorated_validate_pepe):
    assert fixture_decorated_validate_pepe('hey')
    with pytest.raises(NestedInitializationException):
        fixture_decorated_validate_pepe(1)


def test_evil_pepe():
    with pytest.raises(PostInitException):
        EvilPepe('a')


def test_annotated_list():
    assert AnnotatedList(**{'a': [1]})
    with pytest.raises(NestedInitializationException):
        AnnotatedList(**{'a': 'a'})
    with pytest.raises(NestedInitializationException):
        AnnotatedList(**{'a': ['a']})


def test_nested_list_decorated(fixture_nested_list,
                               fixture_decorated_validate_pepe):
    pepe_object = fixture_decorated_validate_pepe('hey')
    decorated_class = dataclass(validate=True)(fixture_nested_list)

    assert decorated_class([[pepe_object]], [[1]])
    with pytest.raises(NestedInitializationException):
        decorated_class([[1]], [[pepe_object]])


def test_nested_dict_decorated(fixture_nested_dict,
                               fixture_decorated_validate_pepe):
    pepe_object = fixture_decorated_validate_pepe('hey')
    decorated_class = dataclass(validate=True)(fixture_nested_dict)

    assert decorated_class({"hello": [pepe_object]}, {"bye": [1]})
    with pytest.raises(NestedInitializationException):
        decorated_class({"hello": ['qwerty']}, {"bye": [1]})


def test_union_lists():
    assert UnitedPepe(**{'a': 1})
    assert UnitedPepe(**{'a': [1]})
    assert UnitedPepe(**{'a': ['1']})


def test_invalid_union_lists():
    with pytest.raises(NestedInitializationException):
        UnitedPepe(**{'a': '1'})


def test_error_list():
    with pytest.raises(NestedInitializationException):
        ErrorLists([DecoratorParams(1)])


def test_uses_validator():
    with pytest.raises(NestedInitializationException):
        UsesValidator(-1)


def test_uses_validators():
    with pytest.raises(NestedInitializationException):
        UsesValidators(-2)


def test_nested_uses_validator():
    input_dict = {'a': {'a': -1}, 'b': {'a': -1}}
    with pytest.raises(NestedInitializationException):
        NestedUsesValidator(**input_dict)


def test_wrong_use_of_validator():
    with pytest.raises(TypeError):
        @dataclass(validate=True)
        class HasInvalidValidator:
            a: int = field(validators='STRING')
