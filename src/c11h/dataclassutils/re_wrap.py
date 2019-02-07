import copy
from dataclasses import (  # type: ignore
    _DataclassParams, dataclass as old_dataclass, MISSING)
from functools import wraps

from c11h.dataclassutils.field import (ExtendedField,
                                       optional_fields_postprocessing)
from c11h.dataclassutils.nesting import nest_dc
from c11h.dataclassutils.util.exceptions import NestedInitializationException
from c11h.dataclassutils.util.helper_functions import ignore_additional_kwargs
from c11h.dataclassutils.validation import (
    check_validators, validate_fields, validate_types)


# we need to extend this class in order to add our custom flags
class _ExtendedDCParams(_DataclassParams):
    __slots__ = ('validate', 'nest', 'ignore_additional_properties')

    def __init__(self, validate, nest, ignore_additional_properties, **kwargs):
        self.validate = validate
        self.nest = nest
        self.ignore_additional_properties = ignore_additional_properties
        super().__init__(**kwargs)

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'init={self.init!r},'
                f'repr={self.repr!r},'
                f'eq={self.eq!r},'
                f'order={self.order!r},'
                f'unsafe_hash={self.unsafe_hash!r},'
                f'frozen={self.frozen!r},'
                f'validate={self.validate!r},'
                f'nest={self.nest!r}'
                f'ignore_additional_properties'
                f'={self.ignore_additional_properties!r}'
                ')')


def _pre_init(cls, ignore_additional_properties, *args, **kwargs):
    """Provide pre-processing funcionallity before the class __init__.

    Optional fields will be taken and checked if they appear in the input, if
    that is negative they will be defaulted according to their
    default_optional_value dinamically.

    If the flag ignore_additional properties will be set, not expected
    arguments will be deleted from the kwargs.

    Args:
        cls: class to be decorated
        ignore_additional_properties: flag to ignore additional properties
        *args: additional args
        **kwargs: given kwargs to initialize the class object.

    Returns:
        defaulted_kwargs: kwargs with defaulted_field if they proceed.

    """
    if ignore_additional_properties:
        kwargs = ignore_additional_kwargs(cls, **kwargs)
    # Optional fields belong to the class, that is why they
    # are not given as args.
    cls_optional_fields = getattr(cls, 'optional_fields')
    defaulted_kwargs = copy.deepcopy(kwargs)
    for f in cls_optional_fields:
        if f.name not in defaulted_kwargs and not hasattr(cls, f.name):
            defaulted_kwargs[f.name] = copy.deepcopy(f.default_optional_value)
    return defaulted_kwargs


def _init_wrapper(__init__, cls, ignore_additional_properties):
    """Wrap around __init__ method.

    This wrapper extends the __init__ to allow two new properties:

    The first one is basically to avoid the use of defaulted args as optional,
    this way we do not loose the capability of non defaulted inheritance.

    The second one is to allow additional properties in the input, they simply
    will be ignored and they will be lost.


    """
    def wrapper(self, *args, **kwargs):
        defaulted_kwargs = _pre_init(cls, ignore_additional_properties,
                                     *args, **kwargs)
        __init__(self, *args, **defaulted_kwargs)
    return wrapper


def _pre_post_init(self, validate, nest):
    """Run the code required by our custom flags.

    Notes:
      - Nesting needs to happen before validation.
      - nest_errors will be collected from nesting and appended to its field.

    """
    nest_errors = {}
    if nest:
        nest_dc(self, nest_errors)
    if validate:
        # type validation
        validate_types(self, nest_errors)
        # custom field validation
        validate_fields(self, nest_errors)
        if nest_errors:
            raise NestedInitializationException(nest_errors)


def _post_init_wrapper(__post_init__, validate, nest):
    """Wrap the existing __post_init__ so that our code gets executed first."""
    @wraps(__post_init__)
    def wrapper(self):
        _pre_post_init(self, validate, nest)
        __post_init__(self)
    return wrapper


def field(*, default=MISSING, default_factory=MISSING, init=True, repr=True,
          hash=None, compare=True, metadata=None, optional=False,
          default_optional_value=None, validators=None):
    """Object to identify dataclass fields.

    Args:
        default: default value of the field
        default_factory: 0 args callable to initialize a default value
        init: If init this field will be added to the __init__
        repr: If repr this field will be added to the __repr__
        hash: If true this will be added to object hash()
        compare: If true, this will used in comparison methods
        metadata: If specified, must be a mapping which is stored but not
            otherwise examined by dataclass.
        optional: If specified, the field will not be required and
            will not be present in the serialization, it will be present
            in the obj instance will the default value if not specified,
            if specified it will appear with the given value.
        default_optional_value: If optional is specified it will be used
            as default value to fill optional values. So when the dataclass
            gets validated or deserialized. If the field value is equal as the
            default_optional_value it will be considered as unspecified
            (not given) and therefore missing.
        validators: A list of callable validator functions which are used to
            validate the field.

    Notes:
        - It is an error to specify both default and default_factory.

    Returns:
        An object to identify a dataclass field.

    """
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory.')

    return ExtendedField(default, default_factory, init, repr, hash, compare,
                         metadata, optional, default_optional_value, validators)


def dataclass(_cls=None, *, init=True, repr=True, eq=True, order=False,
              unsafe_hash=False, frozen=False, validate=False, nest=False,
              ignore_additional_properties=False):
    """Wrap dataclass decorator to perform validation and nesting.

    This wrapper is made in top of python dataclass wrapper to be able to
    extend its capabilities.

    Notes:
        - Every class which has been wrapped with this decorator will follow
        each attribute (Custom class instances, Lists, Dicts and basic data
        types) and perform recursive valdiation in them.

        - This decorator is retro compatible, which means that if a decorated
        class with this wrapper owns an object from the standard dataclass it
        will not lead to any trouble, it will just be skipped.

        - If a decorated class with this wrapper is set with the flag
        validate=True and it owns an object which is also decorated with this
        wrapper and is set with the flag validate=False, an
        InvalidClassCompatibility will be raised.

        - If optional is fields are specified, they will not be added as a
        default variables in the __init__. The __init__ will be decorated
        so the missing values for the defaults will be added
        according to the default_optional_value. So no optional variable will
        be defaulted if not specified in the __init__.

    Args:
        _cls: Class that will be wrapped.
        init: Automatically create __init__ method.
        repr: Automatically generate __repr__ with the class name and all the
            fields.
        eq: If true the __eq__ method will be generated to perform comparison.
        order: If true __lt__, __le__, __gt__, __ge__ will be generated.
        unsafe_hash: If false a __hash__ method will be generated according to
            how eq and frozen are set.
        frozen: If true, to change a field once that the object has been
            instantiated will read to an exception. This emulates read-only
            frozen instances.
        validate: Custom flag -- if true, an automatic validation will be
            performed on all values, given their annotation.
        nest: Custom flag -- if set to true, the constructor will also accept
            dictionaries in stead of nestable dataclasses.
        ignore_additional_properties: if set, additional properties (attributes)
            given to the __init__ constructor will be ignored.

    """
    @wraps(old_dataclass)
    def wrapper(cls):
        # wrap post_init (supply a dummy if there is none) with pre_post_init
        try:
            __post_init__ = cls.__post_init__
        except AttributeError:
            __post_init__ = lambda *args: None  # noqa: E731
        cls.__post_init__ = _post_init_wrapper(__post_init__, validate, nest)

        # this is essentially super().__init__
        old_dataclass(_cls=cls, init=init, repr=repr, eq=eq, order=order,
                      unsafe_hash=unsafe_hash, frozen=frozen)

        # validation of custom validator functions
        check_validators(cls)

        # Get optional fields.
        optional_fields_postprocessing(cls)

        # Wrap the __init__ method to support optional params.
        cls.__init__ = _init_wrapper(cls.__init__, cls,
                                     ignore_additional_properties)

        # extend the dataclass parameter object last, else it gets overwritten
        dc_params = {attr: getattr(cls.__dataclass_params__, attr) for attr in
                     cls.__dataclass_params__.__slots__}
        cls.__dataclass_params__ = _ExtendedDCParams(
            validate, nest, ignore_additional_properties, **dc_params)
        return cls

    if _cls is None:
        # Handle being called with or without parens: We're called with parens.
        return wrapper
    return wrapper(_cls)
