from typing import List

from c11h.dataclassutils.re_wrap import dataclass
from c11h.dataclassutils.util.exceptions import NestedInitializationException


@dataclass(nest=True, validate=True)
class C:
    c_value: int


@dataclass(nest=True, validate=True)
class B:
    b_value: int
    c: C


@dataclass(nest=True, validate=True, ignore_additional_properties=True)
class A:
    a: int
    b: List[B]
    k: List[int]


data = {'a': '2',
        'b': [
            {'b_value': '1', 'c': {'c_value': 1}},
            {'b_value': '2', 'c': {'c_value': '1'}}
        ],
        'k': [1, 2, 'a']}


def test_list_path():
    try:
        A(**data)
    except NestedInitializationException as e:
        assert e.errors['b'][0]
        assert e.errors['b'][1]
        assert e.errors['k'][2]


def test_nested_dict_path():
    try:
        A(**data)
    except NestedInitializationException as e:
        assert e.errors['a']
        assert e.errors['b'][1]['c']['c_value']
