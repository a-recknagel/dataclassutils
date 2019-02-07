from collections.abc import Iterable
from enum import Enum
from logging import getLogger
from typing import _SpecialForm, Callable, Dict, List, Union

log = getLogger(__name__)


def _type_walker(obj, f_name, f_type, actual_value,  # noqa: C901
                 mistakes, f_meta=None):
    """Check on the given type of each field will be applied.

    This function will check recursively Dict and List, for trivial types
    it will be just applied once.

    Args:
        f_name: Name of the field that we will check.
        f_type: Specified type of the field.
        actual_value: Given value for the field.
        mistakes: List of typing errors that will be gathered.
        f_meta: Meta information about the field used for
            custom field validation.

    Notes:
        - Type Union does not support nesting typing, which means that given
        the example: Union[int, List[int]] will not work. The List type has to
        be untyped, which will lead to the following: Union[int, List].

    """
    def inner_check_compatibility():
        """Check if there is a dangerous ownership in the class.

        If a validate dataclass owns an object from another dataclass which
        has been decorated with out custom dataclass flag and the validate flag
        has not been defined or has been defined as False, that will lead to
        a dangerous ownership and user must be aware of that. Because the
        dataclass could be seen as valid but it could have an invalid dataclass
        as an argument.



                 Validate|       |       | not    | <--- composite class
                   Flag  | False | True  | defined|      has validate flag
                 +=======+=======+=======+========|
        owner->  | False | pass  | pass  | pass   | <----the default
                 +-------+-------+-------+--------|
                 | True  | log   | pass  | pass   |
                 +=======+=======+================+

        """
        try:
            validate = f_type.__dataclass_params__.validate
        except AttributeError:
            pass
        else:
            if not validate:
                log.debug(
                    f'The field {f_name} is typed as class: '
                    f'{f_type} and it is incompatible with the class '
                    f'{obj.__class__}. But that class is defined '
                    f'with the flag @dataclass(validate=False) and to be '
                    f'compatible must be set to true.')
    if f_meta:
        log.debug("Meta type custom validation is not supported (yet).")
        return

    inner_check_compatibility()

    if isinstance(f_type, _SpecialForm):
        log.debug(f"SpecialForm Type: '{f_type}' can not be handled (yet).")
        return

    try:
        # Lists and dictionaries must be handled in a different way,
        # since we want to check them in an iterable way.
        given_type = f_type.__origin__
    except AttributeError:
        # If they have no origin they are basic types and our journey
        # trough the nested collection is about to end :(

        # If the given type does not have origin, it wont be List or Dict,
        # so we are not going to handle them.
        given_type = f_type
        # To handle enums we will check if the given value is among the enum
        # values.
        if type(f_type) == type(Enum):
            if type(actual_value) != f_type:
                mistakes.append((f_name, actual_value, f_type))
            else:
                return
        if repr(f_type) == '~T':
            return  # untyped list, nothing to do
        else:
            if not isinstance(actual_value, f_type):
                mistakes.append((f_name, actual_value, f_type))

    if given_type is list:
        if not isinstance(actual_value, list):
            mistakes.append((f_name, actual_value, f_type.__origin__))
            return
        l_type = f_type.__args__[0]
        try:
            for i in actual_value:
                _type_walker(obj, f_name, l_type, i, mistakes)
        except TypeError:
            # If object is not iterable just one more check will be applied.
            return _type_walker(obj, f_name, l_type, actual_value, mistakes)
    elif given_type is dict:
        if not isinstance(actual_value, dict):
            mistakes.append((f_name, actual_value, f_type.__origin__))
            return
        t_key, t_value = f_type.__args__
        for k, v in actual_value.items():
            if not isinstance(k, t_key):
                mistakes.append((f_name, k, t_key))
            # We are taking into consideration
            # that nested values will only appear in the values
            # of the dictionary, not in the keys.
            # If the key has args we follow them.
            if hasattr(t_value, '__args__'):
                return _type_walker(obj, f_name, t_value, v, mistakes)
            else:
                if not isinstance(v, t_value):
                    mistakes.append((f_name, v, t_value))
    elif given_type is Union:
        types = list(f_type.__args__)
        # Preprocessing to handle List as list
        if List in types:
            types.append(list)
        for t in types:
            try:
                origin_type = t.__origin__
            except AttributeError:
                if type(actual_value) is t:
                    break
            else:
                if type(actual_value) is origin_type:
                    # The type matches.
                    if repr(t.__args__[0]) == '~T':
                        # Untyped.
                        break
                    else:
                        # Typed.
                        typed_type = t.__args__[0]
                        if isinstance(actual_value, Iterable):
                            # We check all the elements of the iterable.
                            if all(True if type(e) is typed_type else False
                                   for e in actual_value):
                                break
                        else:
                            if type(actual_value) is typed_type:
                                break
        else:
            mistakes.append((f_name, actual_value, f_type))
    else:
        log.debug(f"The given type is currently not supported: "
                  f"Field: '{f_name}', Type: '{f_type}'")


def validate_types(obj, nest_errors: Dict):  # noqa: C901
    """Validate whether data field types are correct.

    This beautiful masterpiece performs partial validation in a typed
    dataclass.

    Args:
        obj: Object which will be validated.
        nest_errors: Dict used to gather errors.

    Notes:
        Attributes which already have failed will be skipped.

    ToDo:
        with the current nested type validation where the position is not
        handled neither by recursion nor index, we cannot retrieve the index
        for nested lists or if the value appears more than once. To be able to
        perform that the nested validation itself needs to be changed.

    """
    invalid_fields = nest_errors.keys()
    type_errors: list = []

    for f_name, f_field in obj.__dataclass_fields__.items():
        # If the field to be validated has already failed in nesting we
        # should skip it.
        if f_name in invalid_fields:
            continue
        actual_value = getattr(obj, f_name)
        # Optional values with 'None' value must be skipped.
        try:
            if (f_field.optional and
                    actual_value == f_field.default_optional_value):
                continue
        except AttributeError:
            pass  # The field is a regular field.
        _type_walker(obj, f_name, f_field.type, actual_value, type_errors)
    # Gather found errors
    for n, a, t in type_errors:
        # If the error happened in a list, we retrieve the position.
        if isinstance(getattr(obj, n), list):
            try:
                pos = getattr(obj, n).index(a)
            except ValueError:
                log.warning(f"The field {n} which contains the value {a} "
                            f"could not be found in {getattr(obj, n)}. "
                            f"The list path will not be collected.")
                nest_errors[n] = (f"'{a}' is of type '{type(a)}'instead "
                                  f"of '{t}' in a non retrievable position")
                continue
            if n not in nest_errors:
                nest_errors[n] = {}
            nest_errors[n][pos] = (f"'{a}' is of type '{type(a)}'"
                                   f"instead of '{t}'")
        else:
            nest_errors[n] = f"'{a}' is of type '{type(a)}' instead of '{t}'"


def validate_fields(obj, nest_errors: Dict):
    """Validate whether custom data fields values are correct.

    This pre post init function will evaluate the custom validators of
    dataclass fields and validate the respective field value.

    Args:
        obj: Object which will be validated.
        nest_errors: Dict used to gather errors.

    """
    invalid_fields = nest_errors.keys()

    for f_name, f_field in obj.__dataclass_fields__.items():
        # If the field to be validated has already failed in nesting we
        # should skip it.
        if f_name in invalid_fields:
            continue
        if getattr(f_field, 'validators', False):
            actual_value = getattr(obj, f_name)
            validators = (f_field.validators
                          if isinstance(f_field.validators, List)
                          else [f_field.validators])
            for validator in validators:
                try:
                    validator(actual_value)
                except AttributeError as e:
                    if f_name not in nest_errors:
                        nest_errors[f_name] = {}
                    nest_errors[f_name] = str(e)


def check_validators(cls):
    """Check type of validators to be Callable.

    Args:
        cls: dataclass

    """
    errors = []
    for f_name, f_field in cls.__dataclass_fields__.items():
        if getattr(f_field, 'validators', False):
            validators = (f_field.validators
                          if isinstance(f_field.validators, List)
                          else [f_field.validators])
            for validator in validators:
                if not isinstance(validator, Callable):  # type: ignore
                    e = f"The validator '{validator}' is not a callable."
                    errors.append((f_name, e))
    if errors:
        msg = [f"{cls.__name__} contains faulty validators for "
               f"fields:"]
        for n, e in errors:
            msg.append(f"\t{n}: '{e}'")
        raise TypeError('\n'.join(msg))
