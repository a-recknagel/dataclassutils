from enum import Enum

import pytest

from c11h.dataclassutils import dataclass
from c11h.dataclassutils.util.exceptions import NestedInitializationException


class MyCoolEnum(Enum):
    pepe = 'frog'


@dataclass(nest=True, validate=True)
class CompositeClass:
    a: MyCoolEnum


def test_composite_enum():
    assert CompositeClass(a=MyCoolEnum.pepe)
    assert CompositeClass(**{'a': 'frog'})

    with pytest.raises(NestedInitializationException):
        CompositeClass(**{'a': 'cat'})
