import json
from logging import config
import sys
import traceback

from c11h.dataclassutils.settings import CWD

log_config_loc = CWD / 'logger_config.json'


def configure_logger():
    try:
        with open(log_config_loc) as conf_file:
            cfg = json.load(conf_file)
    except (IsADirectoryError, IOError, FileNotFoundError, PermissionError,
            ValueError) as e:
        print(f"Something went wrong while loading the logger config at "
              f"'{log_config_loc}'. Make sure it exists and is well-formed. "
              f"Using NullHandler instead.", file=sys.stderr)
        traceback.print_tb(e.__traceback__, file=sys.stderr)
        cfg = {
            'version': 1,
            'disable_existing_loggers': True,
            'handlers': {
                'null': {'level': 'DEBUG', 'class': 'logging.NullHandler'}
            }
        }
    config.dictConfig(cfg)
