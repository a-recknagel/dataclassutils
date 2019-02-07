from typing import Optional

import pytest

from c11h.dataclassutils.nesting import asdict
from c11h.dataclassutils.re_wrap import dataclass, field
from c11h.dataclassutils.util.exceptions import NestedInitializationException


@dataclass(validate=True, nest=True)
class OptionalTyping:
    a: Optional[str]


@dataclass(validate=True, nest=True)
class OptionalField:
    a: str = field(optional=True)


@dataclass(validate=True, nest=True)
class OptionalFieldCustomDefault:
    a: str = field(optional=True, default_optional_value='0')
    a_typing: Optional[str]


@dataclass(validate=True, nest=True)
class OptionalInheritField(OptionalFieldCustomDefault):
    b: str
    c: str = 'a'


@dataclass(validate=True, nest=True)
class Basic:
    b: int


@dataclass(validate=True, nest=True)
class BasicComposite:
    a: Optional[Basic]


@dataclass(validate=True, nest=True)
class BasicOptional:
    b: Optional[int]


@dataclass(validate=True, nest=True)
class BasicOptionalComposite:
    a: BasicOptional = field(optional=True)


def test_optional_typing():
    obj = OptionalTyping()
    assert obj.a is None


def test_optional_field():
    obj = OptionalField()
    assert obj.a is None


def test_optional_field_custom():
    obj = OptionalFieldCustomDefault()
    assert obj.a == '0'
    assert obj.a_typing is None


def test_optional_inherit_field():
    obj = OptionalInheritField(**{'b': 'test'})
    assert obj.b == 'test'


def deserialize_optional():
    obj = OptionalInheritField(**{'b': 'test'})
    assert obj.a == '0'
    assert asdict(obj) == {'b': 'test', 'c': 'a'}


def test_optional_validation_exception():
    data = {'a': 1}
    with pytest.raises(NestedInitializationException):
        OptionalTyping(**data)
    with pytest.raises(NestedInitializationException):
        OptionalField(**data)


def test_basic_composite():
    obj = BasicComposite()
    assert obj.a is None
    obj = BasicComposite(**{'a': {'b': 1}})
    assert obj.a.b == 1


def test_basic_optional_composite():
    obj = BasicOptionalComposite()
    assert obj.a is None
    obj = BasicOptionalComposite(**{'a': {}})
    assert obj.a.b is None
