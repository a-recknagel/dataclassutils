from dataclasses import _FIELD, Field  # type: ignore
from typing import Union


class ExtendedField(Field):
    __slots__ = ('optional',
                 'default_optional_value',
                 'validators'
                 )

    def __init__(self, default, default_factory, init, repr, hash, compare,
                 metadata, optional, default_optional_value, validators):
        """Extension of dataclass object 'Field'.

        This class adds and extend python core dataclass field in order to
        extend it with additional: optional and default_optional_value.

        """
        self.optional = optional
        self.default_optional_value = default_optional_value
        self.validators = validators
        super().__init__(default, default_factory, init, repr, hash, compare,
                         metadata)

    def __repr__(self):
        return ('Field('
                f'name={self.name!r},'
                f'type={self.type!r},'
                f'default={self.default!r},'
                f'default_factory={self.default_factory!r},'
                f'init={self.init!r},'
                f'repr={self.repr!r},'
                f'hash={self.hash!r},'
                f'compare={self.compare!r},'
                f'metadata={self.metadata!r},'
                f'optional={self.optional},'
                f'default_optional_value={self.default_optional_value},'
                f'_field_type={self._field_type}'
                ')')


def optional_fields_postprocessing(cls):
    """Handle optional fields post processing.

    After the dataclass has been decorated, we want to handle optional fields
    so optional fields are actually handled as optional without being
    defaulted.

    Notice that __dataclass_fields__ is a mappingproxy, so it can not be
    deepcopied and therefore must be edited directly. So this function will
    override and change the given class __dataclass_fields__ and set an
    additional class field called optional_fields which the list of
    the optional fields.

    """
    cls_optional_fields = []
    for k, f in cls.__dataclass_fields__.items():
        optional_field = False
        if isinstance(f, ExtendedField) and f.optional:
            cls_optional_fields.append(f)
        try:
            if f.type.__origin__ is Union and type(None) in f.type.__args__:
                optional_field = True
        except AttributeError:
            continue
        if optional_field:
            extended_field = ExtendedField(f.default, f.default_factory,
                                           f.init, f.repr, f.hash,
                                           f.compare, f.metadata,
                                           optional=True,
                                           default_optional_value=None,
                                           validators=None)
            # Keep the name, type of the field and the real field identifier.
            extended_field.name = k
            extended_field._field_type = _FIELD
            extended_field.type = f.type
            # Collect the optional fields and override the __dataclass_fields__
            cls_optional_fields.append(extended_field)
            cls.__dataclass_fields__[k] = extended_field

    setattr(cls, 'optional_fields', cls_optional_fields)
