from collections.abc import Iterable
import copy
from dataclasses import _is_dataclass_instance, fields  # type: ignore
from enum import Enum
from logging import getLogger
import typing as ty

from c11h.dataclassutils.util.exceptions import NestedInitializationException

log = getLogger(__name__)

LIST_TYPES = {ty.Deque._name, ty.List._name, ty.Set._name,  # type: ignore
              ty.Generator._name}  # type: ignore
DICT_TYPES = {ty.Counter._name, ty.Dict._name,  # type: ignore
              ty.DefaultDict._name}  # type: ignore
SET_TYPES = {ty.FrozenSet._name, ty.Set._name}  # type: ignore
# no need to include NamedTuple here since it's not a _GenericAlias
IMMUTABLE_TYPES = {ty.FrozenSet._name, ty.Tuple._name}  # type: ignore


def nest_dc(dc, nest_errors: ty.Dict):  # noqa: C901
    """If a field is annotated as nestable, turn its dictionary into a class.

    This function makes annotation relevant by parsing it during object
    creation and packaging parameter dictionaries into the annotated
    Nestable class. This means that multi-composite combinations of
    dataclasses don't require manual building of the contained dataclasses
    bottom-up, since it happens automatically.

    Note:
        * This function will obviously not work with dataclasses that use
          __slots__, since they 1) usually don't have a __dict__, and 2)
          are immutable. There is a way to still kind of get it to work by
          calling a classmethod for __slot__ dataclasses instead which runs the
          internal function on the **kwargs instead.
          There are usability caveats though, like such a class then not
          accepting *args, the overall hackiness of the implementation, and the
          fact that it only reflects changes for attributes contained in
          mutables. But ugly != impossible, so if the need ever arises, check
          out !4 for a prototype.

    Args:
        dc: A dataclass instance with the setting nest=True. Its internal
            dictionary will get mutated during the nesting.
        nest_errors: Dict used to gather errors for each attempt of recursive
            initialization.

    """
    def pack_nestables(struct, ref, anno, idx=None):
        # pack parameter dictionaries if they are annotated as nestable
        try:
            nestable = anno.__dataclass_params__.nest
        except AttributeError:
            pass
        else:
            pos_ref = idx if idx is not None else ref
            if nestable and isinstance(struct[pos_ref], dict):
                try:
                    struct[pos_ref] = anno(**struct[pos_ref])
                except NestedInitializationException as e:
                    # To preserve the index in nested list initialization
                    # we need to check if we are given and index and if so,
                    # append the nested key.
                    if idx is not None:
                        # Safe guard
                        if ref not in nest_errors:
                            nest_errors[ref] = {}
                        nest_errors[ref][idx] = e.errors
                    else:
                        nest_errors[ref] = e.errors
        # Instantiate Enums
        if type(anno) is type(Enum):
            try:
                struct[ref] = anno(struct[ref])
            except ValueError:
                pass
            finally:
                return

        # skip over builtins, 'ty.Any', and 'ty.NamedTuple' ...
        if not isinstance(anno, ty._GenericAlias):
            return
        # ... which means that accessing '_name' is now safe to do
        name = anno._name

        # handle typed lists
        if name in LIST_TYPES:
            t = anno.__args__[0]
            if repr(t) == '~T':
                return  # untyped list, nothing to do
            # If the given value to the list is not Iterable
            # we can not instantiate it.
            if not isinstance(struct[ref], Iterable):
                return
            for idx in range(len(struct[ref])):
                pack_nestables(struct[ref], ref, t, idx)
            return

        # handle typed dictionaries
        if name in DICT_TYPES:
            t = anno.__args__[1]
            if repr(t) == '~T':
                return  # untyped dict values, nothing to do
            for key in struct[ref]:
                pack_nestables(struct[ref], key, t)
            return

        # log debug messages for fallthrough and exceptions
        if name in SET_TYPES or name in IMMUTABLE_TYPES:
            log.debug(f"Halting the packing of {anno} since potential "
                      f"parameter lists would be unhashable or immutable.")
        else:
            log.debug(f"Can't handle type {anno} yet.")

    # call the nesting once for each attribute
    for field, field_annotation in dc.__dataclass_fields__.items():
        # We need to handle union types.
        annotation = field_annotation.type
        annotation_list: list = []
        try:
            if annotation.__origin__ is ty.Union:
                annotation_list = annotation.__args__
        except AttributeError:
            pass
        for union_annotation in annotation_list:
            pack_nestables(dc.__dict__, field, union_annotation)
        pack_nestables(dc.__dict__, field, annotation)


def _asdict_inner(obj, dict_factory):
    """Deserialize a dataclass into a dict_factory.

    It is still called _asdict_inner because it actually extends the
    functionality of the one which is used in dataclasses, but the behavior
    is changed in order to support optional fields.

    Notes:
        - If their value is equal to the defaulted optional value it
            will not appear in the deserialization.

    Args:
        obj: dataclass instance to be deserialized.
        dict_factory: If given it will be used instead of buildt-in dict.

    Returns:
        Deserialized class in the given dict_factory.

    """
    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            try:
                # Optional fields which have the default_optional_value are
                # considered not defined and therefore they should not appear
                # on the deserialization.
                if f.optional and getattr(
                        obj, f.name) == f.default_optional_value:
                    continue
            except AttributeError:
                log.debug("A standard dataclass field is being deserialized")
            value = _asdict_inner(getattr(obj, f.name), dict_factory)
            result.append((f.name, value))
        return dict_factory(result)
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_asdict_inner(v, dict_factory) for v in obj)
    elif isinstance(obj, dict):
        return type(obj)(
            (_asdict_inner(k, dict_factory), _asdict_inner(v, dict_factory))
            for k, v in obj.items())
    else:
        if isinstance(obj, Enum):
            return copy.deepcopy(obj.value)
        else:
            return copy.deepcopy(obj)


def asdict(obj, *, dict_factory=dict):
    """Deserialize a dataclass instance.

    Return the fields of a dataclass instance as a new dictionary mapping
    field names to field values.

    Example usage:

      @dataclass
      class C:
          x: int
          y: int

      c = C(1, 2)
      assert asdict(c) == {'x': 1, 'y': 2}

    If given, 'dict_factory' will be used instead of built-in dict.
    The function applies recursively to field values that are
    dataclass instances. This will also look into built-in containers:
    tuples, lists, and dicts.
    """
    if not _is_dataclass_instance(obj):
        raise TypeError("asdict() should be called on dataclass instances")
    return _asdict_inner(obj, dict_factory)
