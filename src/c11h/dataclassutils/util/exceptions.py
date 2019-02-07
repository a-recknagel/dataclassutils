from typing import Dict


class NestedInitializationException(Exception):

    def __init__(self, errors: Dict):
        """Collect and raise errors in the __pre_post_init.

        Gather information about errors that happened during validation
        and composite fields initialization. Building an error message
        recursively.
        """
        self.errors = errors
