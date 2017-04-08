try:
    from molotov.api import (scenario, setup, global_setup, teardown,  # NOQA
                             global_teardown)                          # NOQA
    from molotov.util import request, json_request                     # NOQA
except ImportError:
    pass   # first import

__version__ = '1.1'
