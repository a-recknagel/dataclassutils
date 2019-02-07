from copy import deepcopy


def ignore_additional_kwargs(cls, **kwargs):
    """Create new kwargs dictionary without unexpected fields."""
    expected_args = cls.__dataclass_fields__.keys()
    cleaned_kwargs = deepcopy(kwargs)
    for key in kwargs.keys():
        if key not in expected_args:
            cleaned_kwargs.pop(key)
    return cleaned_kwargs
