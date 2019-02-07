def is_greater_0(i: int):
    """Check if a given integer is greater than 0."""
    if i < 0:
        raise AttributeError("The given integer is not greater than 0.")


def is_odd(i: int):
    """Check if a given integer is an odd number."""
    if i % 2 == 0:
        raise AttributeError("The given integer is not an odd number.")
